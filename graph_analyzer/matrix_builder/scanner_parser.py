#Cloudboobk parser v1.0
import ply.lex as lex
from ply.lex import TOKEN
import re
import parser
import token
import math

tokens = ['IMPORT','FUN_DEF','COMMENT','LOOP_FOR','LOOP_WHILE','IF','ELSE','TRY','EXCEPT','PRINTV2', 'PRINTV3','FUN_INVOCATION','PYTHON_INVOCATION',
'INVOCATION','ASSIGNATION']

#fundefintion =r'[\s]*[d][e][f][\s]*'+r'[a-zA-Z_][a-zA-Z_0-9]*'+r'[\s]*[(][\d\D\s\S\w\W]*[)][\s]*[:][\n]*'
fundefintion =r'[d][e][f][\s]*'+r'[a-zA-Z_][a-zA-Z_0-9]*'+r'[\s]*[(][\d\D\s\S\w\W]*[)][\s]*[:][\n]*'
t_ignore = " \n"
opt = r'[i][m][p][o][r][t]|[f][r][o][m]'
iden = r'[a-zA-Z_][a-zA-Z_0-9]*'
importation = r'[i][m][p][o][r][t]'+r'[\s]+'+r'[a-zA-Z_][a-zA-Z_0-9]*'#+r'[\s]+'+r'[[a][s][\s]+[a-zA-Z_][a-zA-Z_0-9]*]*'
fromimport = r'[f][r][o][m]'+r'[\s]'+iden+importation #Not implemented, how to save in database

#functions = []
#fun_invocations = []
#token_list = []



def t_COMMENT(t):
	r'\#.*'
	pass

@TOKEN(importation)
def t_IMPORT(t):
	t.type = 'IMPORT'
	return t

def t_PRINTV3(t):#TODO Probarlo mas.
	r'[p][r][i][n][t][ ]*[(]["][@][\d\D\s\S\w\W]*'
	t.type = 'PRINTV3'
	return t

def t_PRINTV2(t):#TODO Probarlo mas.
	r'[p][r][i][n][t][ ]["][@][\d\D\s\S\w\W]*'
	t.type = 'PRINTV2'
	return t

@TOKEN(fundefintion)
def t_FUN_DEF(t):#decorators not observed
    #r'[d][e][f][\s]+[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = 'FUN_DEF'
    t.value = t.value.split(" ")[1]
    #t.value = t.value.replace('\t','')
    t.value = re.sub(r'\s*',"",t.value)
    #t.value = t.value.split("(")[0]
    return t

def t_LOOP_FOR(t):#very simple for, not evaluated targetlist
	#r'[\s]*[f][o][r][\s]+[\d\D\s\S\w\W][\s]+[i][n][\s]+[\d\D\s\S\w\W]+'
	r'[f][o][r][\s]+[\d\D\s\S\w\W][\s]+[i][n][\s]+[\d\D\s\S\w\W]+'
	t.type = 'LOOP_FOR'
	t.value = t.value.split(" ")[3]
	t.value = t.value[:len(t.value)-2]
	#value = len(eval(loop_st[left:right]))
	try:
		t.value = len(eval(t.value))#only this kind of iterator?
	except:
		t.value = 100
	return t

def t_LOOP_WHILE(t):
	r'[w][h][i][l][e][\s]+[\d\D\s\S\w\W]*'
	t.type = 'LOOP_WHILE'
	t.value = 100
	return t

def t_IF(t):
	r'[i][f][\s]+[\d\D\s\S\w\W]+[:][\s]*[\n]'
	t.type = 'IF'
	t.value = 1
	return t

def t_ELSE(t):
	r'[e][l][s][e][\s]*[:][\s]*[\n]'
	t.type = 'ELSE'
	t.value = 1
	return t

def t_TRY(t):
	r'[t][r][y][\s]*[:][\s]*[\n]'
	t.type = 'TRY'
	t.value = 1
	return t

def t_EXCEPT(t):
	r'[e][x][c][e][p][t][\s]*[:][\s]*[\n]'
	t.type = 'EXCEPT'
	t.value = 1
	return t

#def t_FUN_INVOCATION(t):
def t_INVOCATION(t):
	#r'[\s]*[a-zA-Z_][a-zA-Z_0-9]*[(][\d\D\s\S\w\W]*[)][\s]*[\n]*'
	r'[a-zA-Z_][a-zA-Z_0-9]*[.]*[a-zA-Z_][a-zA-Z_0-9]*[(][\d\D\s\S\w\W]*[)][\s]*[\n]*'#initial part, complete invocation
	#print('Trad invocation:',t.value)
	#t.value = t.value[:len(t.value)-1]
	if (t.value.find("\n")!=-1):
		t.value = t.value.replace("\n","") 
	else:
		t.value = t.value
	#print('Trad invocation:',t.value)
	t.value = re.sub(r'[(][\d\D\s\S\w\W]*[)][\s]*',"",t.value)
	#print('Trad invocation:',t.value)
	t.value = re.sub(r'\s*',"",t.value)
	t.type = 'INVOCATION'
	return t

def t_ASSIGNATION(t):
	r'[a-zA-Z_][a-zA-Z_0-9]+[/s]*[=][/s]*'
	t.type = 'ASSIGNATION'
	#t.value removing tabs
	t.value = re.sub(r'\s*',"",t.value)
	return t

def t_error(t):
    #print("Illegal characters!")
    t.lexer.skip(1)

def tokenize(file):
	token_list = []
	lexer = lex.lex()

	with open(file,'r') as fi:
	    
	    for i,line in enumerate(fi,start=1):
	        lexer.input(line)
	        #indent level: only if tabs before text, not counted else
	        indent_level = line.count('\t')

	        cont = True
	        while cont:
	            tok = lexer.token()
	            if not tok:
	                #cont = False
	                break 
	            tok.lineno = i
	            #print(tok)
	            token_list.append(tok)

	return token_list

def function_scanner(tokens,dir,file,function_names):
	#token_list = tokenize()
	#function_names = []
	for i in tokens:
		if i.type == 'FUN_DEF':
			file = file.replace(".py","")
			#function_names.append(dir+"."+file+"."+i.value.split("(")[0])#cutre
			if dir!="":
				function_names.append(dir+"."+file+"."+i.value.split("(")[0])#cutre
			else:
				if i.value.split("(")[0] == 'main':
					function_names.insert(0,file+"."+i.value.split("(")[0])
				else:
					function_names.append(file+"."+i.value.split("(")[0])#cutre
			#i.value = i.value.split("(")[0]
	#return function_names
