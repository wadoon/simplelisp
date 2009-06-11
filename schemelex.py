#!/usr/bin/python
# -*- coding: utf-8 -*-

import ply.lex as lex

tokens = (
    'LPAREN',
    'RPAREN',      
    'SEPERATOR',
    'VAR',
    'LITERAL',
    'NUM'
)

t_SEPERATOR     = r'[ \t]+'
t_VAR           = r'[a-zA-Z_.$+\-*/%!§=\']\w*'
t_LITERAL       = r'"[a-zA-Z0-9_+\*\- :, ]*"'
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
#t_NUM =

def t_NUM(t):    
    r'\d+(\.\d+)?'
    try:
        t.value=float( t.value )
        return t
    except:
        print "Line %d: Number %s is not an int!" % (t.lineno,t.value)

def t_newline(t):
    r'\n'
    t.lineno += 1

#t_ignore=' \t'

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

lex.lex()

if __name__=='__main__':
    data = raw_input()
    lex.input(data)
    
    while True:
        tok = lex.token()
        print tok
        if not tok:
            break;
