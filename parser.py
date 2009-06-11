import ply.yacc as yacc
from pprint import pprint
from schemelex import tokens


_var_names = {
    'print':pprint,
    'p':pprint,
    'list':lambda: tuple('abcdefghijklmnopqrstuvwxyz'),
    'NIL':None,
    'a':'Test Variable',
    'x':1,
    'y':2,
}

def register(*args):
    for fn in args:
        name = fn.__doc__.splitlines()[0].strip()
        _var_names[name]=fn

### Build in functions
def add(*args):
    "+"
    return reduce(lambda x,y: x+y , args)

def sub(*args):
    "-"
    return reduce(lambda x,y: x-y, args)

def mul(*args):
    "*"
    return reduce(lambda x,y: y*x, args)

def div(*args):
    "/"
    return reduce(lambda x,y: x/y,args)

def floordiv(*args):
    "//"
    return reduce(lambda x,y:x//y,args)

def car(*args):
    "car"
    return args[0]

def set(*args):
    "set"
    _var_names[args[0]]=args[1]

def delete(*args): 
    "del"
    for a in args: del _var_names[a]
    

register(add,sub,mul,div,set,floordiv,car,delete)

################################################################# 


precedence = (
    ('right' ,'RPAREN'),
    ('left' ,'LPAREN'),
    ('right' , 'VAR'),
    ('right' , 'LITERAL'),
    ('right' , 'NUM')
)


class Value(object):
    def __init__(self,val):
        if isinstance(val, (str,unicode)):
            val = val.strip('"')
        self.val = val

    def __call__(self):
    #    print "Call: " + self.val
        return self.val

    def __repr__(self):
        return "Value(%s)" % self.val

class Variable(Value):
    def __call__(self):
        return _var_names[self.val];

class List(object):
    def __init__(self, name, exprlist):
        self.name = _var_names[name]
        self.exprlist = exprlist
        
    def __call__(self):   
        param = [ x() for x in self.exprlist]
        #pprint(param)
        return self.name(*param)
        

pl = lambda list:  ', '.join( (str(x) for x in  list ))

start = 'inputstream'

def p_error(t):
    print >> sys.stderr, "ERR:" , t,
    print >> sys.stderr, "Line: %d, %d" %(  t.lineno, t.lexpos )
    print >> sys.stderr, "type: %s, value: %s" %(  t.type , t.value )
    
    print t.lexer.skip(1)


def p_var(t):
    "var : VAR"
    t[0] = Variable(t[1])
    return t

def p_atom(t):
    '''atom : LITERAL
            | NUM
    '''
    t[0] = Value( t[1] )
    return t

def p_expr(t):
    '''expr : list 
            | var
            | atom
            '''
   # print "expr : %s" % pl(t)                       
    t[0] = t[1]
    return t

def p_exprlist(t):
    '''exprlist : exprlist SEPERATOR expr
                | expr'''
#    print "exprlist : %s " % pl(t)
    try:
        t[0] = t[1] + [t[3],]
    except IndexError,e:
        t[0] = [t[1]]
    return t

def p_list(t):
    '''list : LPAREN VAR SEPERATOR exprlist RPAREN'''
 #   print "list : %s " % pl(t)
    t[0] = List(t[2],t[4])
    return t

def p_inputstream(t):
    '''inputstream : list SEPERATOR inputstream
                   | list inputstream
                   | list'''
    t[0] = [t[1]]

    try:
        t[0]+=t[2]
    except:
        pass    
    return t

yacc.yacc()

if __name__=='__main__':
    import sys

    if sys.argv[1]:
        s = sys.argv[1]
    else:
        s = raw_input('calc > ')
    result = yacc.parse(s)
#    print result
    [x() for x in result]
    
    
