#!/usr/bin/python

import ply.yacc as yacc
from pprint import pprint
from schemelex import tokens


DEBUG=False

_var_names = {
    'out':pprint,    
    'NIL':None,
    'True': True,
    'False': False,
    'T':True,
    'F':False
}

def register(*args):
    for fn in args:
        name = fn.__doc__.splitlines()[0].strip()
        _var_names[name]=fn
        _var_names[fn.func_name]=fn

class newnamespace(object):
    def __init__(self, fun):
        self.fun = fun
        self.__doc__ =   ""
        self.func_name = ""
        
    def __call__(self,*args):
        global _var_names
        globalns = _var_names
        
        #declare all function in new namespace        
        _var_names=dict( [ t for t in globalns.iteritems() if callable(t[1]) ] )
        print "change namespace %s => %s" % (len(globalns),  len(_var_names))
        result = self.fun(*args)        
        _var_names = globalns
        return result

      

def lisp(fn):
    if DEBUG: d = debug
    else:     d = lambda x:x
    register(d(fn))
    return fn


class values(object):
    def __init__(self, fn):
        self.fn = fn
        self.__doc__ = fn.__doc__
        self.func_name = fn.func_name
        
    def __call__(self, *args):
        params = [x() for x in args]
        return self.fn(*params)

def debug(fn):
    class debug_x(object):
        def __init__(self, fn):
#            print "activeated for %s " % fn.func_name
            self.fn = fn
            self.func_name = fn.func_name
            self.__doc__ = fn.__doc__
            
        def __call__(self, *args):            
            a = self.fn(*args)
            print 'call %s (%s) = %s' % ( fn.func_name, str(args) , str(a))
            return a        
    return debug_x(fn)
        
        

### Build in functions
@lisp
@values
def _and(*args):
    "and"
    return all(args)


@lisp
@values
def _or(*args):
    "or"
    return any(args)


@lisp
@values

def inverseb(*args):
    "not"
    return [ not x for x in args]


@lisp
@values

def lt(*args):
    "lt"
    for i in xrange(len(args)-1):
        if args[i] >= args[i+1]:
            return False
    return True


@lisp
@values

def gt(*args):
    "gt"
    for i in xrange(len(args)-1):
        if args[i] <= args[i+1]:
            return False
    return True


@lisp
@values
def eq(*args):
    "="
    for i in xrange(len(args)-1):
        if args[i] != args[i+1]:
            return False
    return True
        


@lisp
def cond(c,a1,a2):
    "if"

    if c():
        a1()
    else:
        try:
            a2()
        except IndexError, e:
            pass

        
@lisp
@values
def out(*args):
    "p"
    for a in args: pprint(a)
    return None


@lisp
@values
def add(*args):
    "+"
    return reduce(lambda x,y: x+y , args)


@lisp
@values

def sub(*args):
    "-"
    return reduce(lambda x,y: x-y, args)


@lisp
@values

def mul(*args):
    "*"
    return reduce(lambda x,y: y*x, args)


@lisp
@values

def div(*args):
    "/"
    return reduce(lambda x,y: x/y,args)


@lisp
@values

def floordiv(*args):
    "//"
    return reduce(lambda x,y:x//y,args)


@lisp
@values
def car(*args):
    "pop"
    return args.pop()

@lisp
@values
def push(*args):
    "push"
    args = list(args)
    if type(args[0]) is list:
        l = args[0]; del args[0]
        for i in args:
            l.append(i)
        return l
    
    elif type(args[len(args)-1]) is list:
        l = args.pop()
        for i in args:
            l.insert(0,i)
        return l
    else:
        return list(args)
    

@lisp
@debug
def setq(*args):
    "set"
    _var_names[args[0]]=args[1]


@lisp
@values
def delete(*args): 
    "del"
    for a in args: del _var_names[a]
    

@lisp
@values
def direnv():
    "dir"
    return _var_names.keys()


@lisp
def _commandlist(*args):
    "cl"
    return args

@lisp
def __createfunc(name, func):
    "def"
    _var_names[ name() ]=debug( newnamespace( func ) )
    return name()
    



#register(add,sub,mul,div,set,floordiv,car,delete)

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
#        print len(  _var_names )
        if self.val in _var_names:
            return _var_names[self.val]
        else:
            print "ERR: %s is not define" % self.val 

class List(object):
    def __init__(self, name, exprlist=False):
        self.name = _var_names[name]
        self.exprlist = exprlist
        
    def __call__(self):   
        #pprint(param)
        if self.exprlist == False:
            return self.name()
        else:
            return self.name(*self.exprlist)
#            param = [ x() for x in self.exprlist]
#            return self.name(*param)
        
        
        

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
    '''list : LPAREN VAR RPAREN
            | LPAREN VAR SEPERATOR exprlist RPAREN
            '''

    #   print "list : %s " % pl(t)
    try:
        t[0] = List(t[2],t[4]) #2nd case
    except IndexError ,e:      #1st case
        t[0] = List(t[2])
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

def reg_module(module):
    for f in dir(module):
        fn = "%s.%s" %( module.__name__, f)
        print "register %s as %s"  %  ( f, fn )
        _var_names[fn]=module.__dict__[f]

def reg_module_s(module):
    __import__(module)
    reg_module(sys.modules[module])


if __name__=='__main__':
    import sys

    import optparse
    o = optparse.OptionParser()
    o.add_option('-m','--module-list',action="store", dest="ml")

    opts, args = o.parse_args()

    if opts.ml:
        for m in opts.ml.split(','):
            reg_module_s(m)    

    if len(args):
        s = ' '.join(args)
        result = yacc.parse(s)
        #    print result
        [x() for x in result]
    else:
        while True:
            try:
                i = raw_input('>')
                if i =='--':break
                result = yacc.parse(i)
                pprint( [x() for x in result] )
            except EOFError, e:
                sys.exit(0)                
            except BaseException, e:
                print e
        

    
    
