#Cloudboobk parser v1.0
import ply.lex as lex
from ply.lex import TOKEN
import re
import parser
import token
import math

#file = "pruebas.py"
#file = "pruebas2.py"
#file = "pruebas3.py"
#file = "nbody.py"
file = "nbody_orig.py"

tokens = ['TEST','IMPORT','FUN_DEF','COMMENT','LOOP_FOR','LOOP_WHILE','IF','ELSE','TRY','EXCEPT','PRINTV2', 'PRINTV3','FUN_INVOCATION','PYTHON_INVOCATION',
'INVOCATION','ASSIGNATION','RETURN','IDEN','GLOBAL']

fundefintion =r'[d][e][f][\s]*'+r'[a-zA-Z_][a-zA-Z_0-9]*'+r'[\s]*[(][\d\D\s\S\w\W]*[)][\s]*[:][\n]*'
funorglobal = r'[d][e][f][\s]*[a-zA-Z_][a-zA-Z_0-9]*[\s]*[(][\d\D\s\S\w\W]*[)][\s]*[:][\n]*|[a-zA-Z_][a-zA-Z_0-9]*'
t_ignore = " \n"
iden = r'[a-zA-Z_][a-zA-Z_0-9]*'


from_token = r'[f][r][o][m][\s]+[a-zA-Z_.][a-zA-Z_0-9.]*'
import_token = r'[i][m][p][o][r][t][\s]+[a-zA-Z_\*][a-zA-Z_0-9]*'
importation = from_token + r'[\s]+' + import_token + r'|' + import_token
iden = r'[a-zA-Z_][.a-zA-Z_0-9]*'
assignation = r'[\s]*[=][\s]*'
global_var = r'^[a-zA-Z_][a-zA-Z_0-9]*|[g][l][o][b][a][l][\s]+[a-zA-Z_][a-zA-Z_0-9]*'

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

'''def t_COMPLEX_IDEN(t):
	r'[a-zA-Z_.][a-zA-Z_0-9]*'
	t.type= 'COMPLEX_IDEN'
	return t'''

@TOKEN(fundefintion)
#@TOKEN(funorglobal)
def t_FUN_DEF(t):#decorators not observed
    #r'[d][e][f][\s]+[a-zA-Z_][a-zA-Z_0-9]*'
	t.type = 'FUN_DEF'
	t.value = t.value.split(" ")[1]
	t.value = re.sub(r'\s*',"",t.value)
	if t.value.find("(")!=-1:
		t.value = t.value.split("(")[0]
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
	r'[a-zA-Z_][.a-zA-Z_0-9]*[.a-zA-Z_][a-zA-Z_0-9]*[(][\d\D\s\S\w\W]*[)][\s]*[\n]*'#initial part, complete invocation
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

def t_RETURN(t):
	r'[\s]*[r][e][t][u][r][n][\s]*[\d\D\s\S\w\W]*[\n]'
	t.type = 'RETURN'
	return t

@TOKEN(assignation)
def t_ASSIGNATION(t):
	#r'[a-zA-Z_][.a-zA-Z_0-9]*[\s]*[=][\s]*'
	t.type = 'ASSIGNATION'
	#t.value removing tabs
	t.value = re.sub(r'\s*',"",t.value)
	return t

@TOKEN(global_var)
def t_GLOBAL(t):
	t.type='GLOBAL'
	if 'global' in t.value:
		t.value = t.value.replace('global','')
		t.value = re.sub(r'\s*',"",t.value)
	t.value = '_VAR_'+t.value
	return t

@TOKEN(iden)
def t_IDEN(t):
	t.type='IDEN'
	return t

'''@TOKEN(complex_iden)
def t_TEST(t):
	t.type='TEST'
	return t'''

def t_error(t):
    #print("Illegal characters!")
    t.lexer.skip(1)

def tokenize(module,file,function_list):
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
	    #normalize token list
	    #if there are several tokens in same line, the pos for everyone will be the minimum position
	    for i,j in enumerate(token_list[:-1]):
	    	if j.lineno == token_list[i+1].lineno:#the next token in the same line
	    		token_list[i+1].lexpos = j.lexpos #get the first lexpos (the one to the left)

	    for i in token_list:
	    	#if (i.type == 'FUN_DEF' or i.type == 'INVOCATION' or i.type == 'GLOBAL'):
	    	if (i.type == 'FUN_DEF' or i.type == 'GLOBAL'):
	    		#print("=======>OJO: "+ i.type + " " + i.value)
	    		for j in function_list:
	    			if i.value in j:
	    				#print("========>OJO: "+i.value+ " y " + j)
	    				i.value = module + "." + i.value
	    	#the module added is all to the left of the last ".". This is for the case in there are two files in 1 dir, we add only de dir
	    	#the invocation already is file.fun, and if there arent more files, the invocation is fun, and the module is the file without "."
	    	#is only added if there is a path
	    	if i.type == 'INVOCATION':
				if module.rfind(".")!= -1:
					module = module[:module.rfind(".")]
					for j in function_list:
						if i.value in j:
							print("========>OJO: "+i.value+ " y " + j)
							i.value = module + "." + i.value
				else:
					for j in function_list:
						if i.value in j:
							print("========>OJO: "+i.value+ " y " + j)
							i.value = module + "." + i.value
				print("Asi queda el token invocation:", i)
	return token_list


def function_scanner_old():
	token_list = tokenize()
	function_names = []
	for i in token_list:
		if i.type == 'FUN_DEF':
			function_names.append(i.value.split("(")[0])#cutre
		if i.type == 'GLOBAL':
			if i.value not in function_names:
				function_names.append(i.value)
	return function_names

def function_parser(token_list,function_names):
	print(">>>Entro en function_parser")
	matrix = create_matrix(function_names)
	invocator = ""
	values = []
	try:
		values[0] = 1
	except:
		values.insert(0,1)
	#levels.append(0)
	for i in token_list:
		#print ("token modulo",i)
		for tok in token_list[i]:
			#print("token:", tok)
			if tok.type == 'FUN_DEF' and tok.value in function_names:#not for classes only procedimental programs
				level = tok.lexpos
				if tok.value.find("(")!=-1:
					invocator = tok.value.split("(")[0]
				else:
					invocator = tok.value
				n = 1
				#values.insert(tok.lexpos,n)
				try:
					values[tok.lexpos] = n
				except:
					values.insert(tok.lexpos,n)
				print("fun definition: ",tok.value  +" values: "+ str(values))
				continue
			#if tok.lexpos > levels[-1]:#ignore indent 0
			if tok.lexpos > 0:#ignore indent 0
				if (tok.type == 'INVOCATION' or tok.type == 'GLOBAL'):
					print("Encuentro: "+ tok.type + " que vale: " + tok.value)
					if tok.value in function_names:
						print("Es de las que busco")
				if (tok.type == 'INVOCATION' or tok.type == 'GLOBAL') and tok.value in function_names:
					print("Invocation", tok.value, tok.lineno)
					index_invocator = function_names.index(invocator)+1
					index_invoked = function_names.index(tok.value)+1
					#before assign value to matrix compare value and indentation
					#if tok.lexpos-levels[-1] == 1:#only if the invocation is the first thing in the function suite
					#	print("Llamada de valor 1",tok.lexpos," y ", levels[-1], tok.lineno)
					#	n = int(1)
					#else:#more indent than one
					#	print("llamada de valor n ",tok.lexpos, tok.lineno)
					#	n = values[tok.lexpos-1]
					print(tok.lexpos-1)
					n = values[tok.lexpos-1]
					matrix[index_invoked][index_invocator] += int(n)
					print("La funcion: "+invocator+" invoca a "+ tok.value + " " + str(n) + " veces")
					#last_value = n
				if tok.type == 'LOOP_FOR':
					#level = tok.lexpos
					#n = n*tok.value
					n = values[tok.lexpos-1]*tok.value
					#values.insert(tok.lexpos,n)
					try:
						values[tok.lexpos] = n
					except:
						values.insert(tok.lexpos,n)
					print("Bucle for, "+ "valores: "+ str(values))
				if tok.type == 'LOOP_WHILE':
					n = n * tok.value
					#values.insert(tok.lexpos,n)
					try:
						values[tok.lexpos] = n
					except:
						values.insert(tok.lexpos,n)
					print("Bucle while"+ "valores: "+ str(values))
				if tok.type == 'IF':
					n = tok.value
					#values.insert(tok.lexpos,n)
					try:
						values[tok.lexpos] = n
					except:
						values.insert(tok.lexpos,n)
				if tok.type == 'ELSE':
					n = 1
					#values.insert(tok.lexpos,n)
					try:
						values[tok.lexpos] = n
					except:
						values.insert(tok.lexpos,n)
				if tok.type == 'EXCEPT':
					n = 1
					#values.insert(tok.lexpos,n)
					try:
						values[tok.lexpos] = n
					except:
						values.insert(tok.lexpos,n)
			if tok.lexpos == 0:#ignore indent 0
				n=1
				try:
					values[tok.lexpos] = n
				except:
					values.insert(tok.lexpos,n)
	print_matrix(matrix)
	return matrix

def parser():
	pass

def create_matrix(function_list):
	num_cols = len(function_list)+1
	num_rows = num_cols
	matrix = [[None] * num_cols for i in range(num_rows)]
	matrix[0][0] = 'Matrix'
	for i in range(1,num_rows):
		matrix[0][i] = function_list[i-1]
	#print matrix[0]
	for i in range(1,num_rows):
		matrix[i][0] = function_list[i-1]
	for i in range(1,num_rows):
		for j in range(1,num_cols):
			matrix[i][j]=0
	return matrix

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])


def complete():
	function_names = function_scanner()
	print(function_names)
	function_parser()

def onlytokens():
	toklist = tokenize()
	for i in toklist:
		if i.type=='IMPORT':
			print(i)

def tokenize_imports(file):
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
	            if tok.type=='IMPORT':
	            	token_list.append(tok)
	    #normalize token list
	    #if there are several tokens in same line, the pos for everyone will be the minimum position
	    for i,j in enumerate(token_list[:-1]):
	    	if j.lineno == token_list[i+1].lineno:#the next token in the same line
	    		token_list[i+1].lexpos = j.lexpos #get the first lexpos (the one to the left)

	return token_list


#onlytokens()
#complete()
