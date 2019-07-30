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
#file = "nbody_orig.py"

tokens = ['TEST','IMPORT','FUN_DEF','COMMENT','LOOP_FOR','LOOP_WHILE','IF','ELSE','TRY','EXCEPT','PRINTV2', 'PRINTV3','FUN_INVOCATION','PYTHON_INVOCATION',
'INVOCATION','ASSIGNATION','RETURN','IDEN','GLOBAL','PARALLEL','RECURSIVE','LOCAL','CLASS_DEF']

fundefintion =r'[d][e][f][\s]*'+r'[a-zA-Z_][a-zA-Z_0-9]*'+r'[\s]*[(][\d\D\s\S\w\W]*[)][\s]*[:][\n]*'
funorglobal = r'[d][e][f][\s]*[a-zA-Z_][a-zA-Z_0-9]*[\s]*[(][\d\D\s\S\w\W]*[)][\s]*[:][\n]*|[a-zA-Z_][a-zA-Z_0-9]*'
t_ignore = " \n"
#iden = r'[a-zA-Z_][a-zA-Z_0-9]*'

from_token = r'[f][r][o][m][\s]+[a-zA-Z_][a-zA-Z_0-9]*'
import_token = r'[i][m][p][o][r][t][\s]+[a-zA-Z_][a-zA-Z_0-9]*'
importation = from_token + r'[\s]+' + import_token + r'|' + import_token
iden = r'[a-zA-Z_][.a-zA-Z_0-9]*'
assignation = r'[\s]*[=][\s]*'
global_var = r'^[a-zA-Z_][a-zA-Z_0-9]*|[g][l][o][b][a][l][\s]+[a-zA-Z_][a-zA-Z_0-9]*'

class_token = r'^[c][l][a][s][s][\s]*' + iden + r'[\s]*[:][\s]+'

def t_PARALLEL(t):
	r'[#][_][_][C][L][O][U][D][B][O][O][K][:][P][A][R][A][L][L][E][L][_][_]'
	t.type='PARALLEL'
	return t

def t_RECURSIVE(t):
	r'[#][_][_][C][L][O][U][D][B][O][O][K][:][R][E][C][U][R][S][I][V][E][_][_]'
	t.type='RECURSIVE'
	return t

def t_LOCAL(t):
	r'[#][_][_][C][L][O][U][D][B][O][O][K][:][L][O][C][A][L][_][_]'
	t.type='LOCAL'
	return t

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

@TOKEN(class_token)
def t_CLASS_DEF(t):#decorators not observed
	t.type = 'CLASS_DEF'
	t.value = re.sub(r'([c][l][a][s][s]|[:]|[\s]*)',"",t.value)
	return t

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
	r'[a-zA-Z_][a-zA-Z_0-9]*[a-zA-Z_][a-zA-Z_0-9]*[(][\d\D\s\S\w\W]*[)][\s]*[\n]*'#initial part, complete invocation
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
	    #normalize token list
	    #if there are several tokens in same line, the pos for everyone will be the minimum position
	    for i,j in enumerate(token_list[:-1]):
	    	if j.lineno == token_list[i+1].lineno:#the next token in the same line
	    		token_list[i+1].lexpos = j.lexpos #get the first lexpos (the one to the left)


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

def function_parser_old():
	print("entro en el parser")
	token_list = tokenize()
	#print(token_list)
	function_names = function_scanner()
	matrix = create_matrix(function_names)
	invocator = ""
	values = []
	try:
		values[0] = 1
	except:
		values.insert(0,1)
	#levels.append(0)
	for tok in token_list:
		if tok.type == 'FUN_DEF':#not for classes only procedimental programs
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
			print(tok.value  +" values: "+ str(values))
			continue
		#if tok.lexpos > levels[-1]:#ignore indent 0
		if tok.lexpos > 0:#ignore indent 0
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


#onlytokens()
#complete()

def tokenize_new(file):
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

def function_scanner(tokens,dir,file,function_names,labels_dict):
	#token_list = tokenize()
	#function_names = []
	file = file.replace(".py","")
	for j,i in enumerate(tokens,1):#numero, token
		if i.type == 'FUN_DEF':
			if i.lexpos != 0:
				continue #avoid translate inner functions of classes or meta functions
			if dir!="":
				function_names.append(dir+"."+file+"."+i.value.split("(")[0])#cutre
				i.value = dir+"."+file+"."+i.value.split("(")[0]
			else:
				if i.value.split("(")[0] == 'main':
					function_names.insert(0,file+"."+i.value.split("(")[0])
					i.value = file+"."+i.value.split("(")[0]
				else:
					function_names.append(file+"."+i.value.split("(")[0])#cutre
					i.value = file+"."+i.value.split("(")[0]
		if i.type == 'GLOBAL':
			if dir!="":
				if dir+"."+file+"."+i.value not in function_names:
					function_names.append(dir+"."+file+"."+i.value)
					i.value = dir+"."+file+"."+i.value
			else:
				if file+"."+i.value not in function_names:
					function_names.append(file+"."+i.value)
					i.value = file+"."+i.value
		if i.type == 'PARALLEL':
			i.value = tokens[j].value #Metemos como valor en el token parallel, la funcion parallel
			#labels_dict[i.value]=i.type
			if dir!="":
				i.value = dir+"."+file+"."+i.value.split("(")[0]
			else:
				if i.value.split("(")[0] == 'main':
					i.value = file+"."+i.value.split("(")[0]
				else:
					i.value = file+"."+i.value.split("(")[0]
			labels_dict[i.value]=i.type
		if i.type == 'RECURSIVE':
			i.value = tokens[j].value #Metemos como valor en el token parallel, la funcion parallel
			#labels_dict[i.value]=i.type
			if dir!="":
				i.value = dir+"."+file+"."+i.value.split("(")[0]
			else:
				if i.value.split("(")[0] == 'main':
					i.value = file+"."+i.value.split("(")[0]
				else:
					i.value = file+"."+i.value.split("(")[0]
			labels_dict[i.value]=i.type
		if i.type == 'LOCAL':
			i.value = tokens[j].value #Metemos como valor en el token parallel, la funcion parallel
			#labels_dict[i.value]=i.type
			if dir!="":
				i.value = dir+"."+file+"."+i.value.split("(")[0]
			else:
				if i.value.split("(")[0] == 'main':
					i.value = file+"."+i.value.split("(")[0]
				else:
					i.value = file+"."+i.value.split("(")[0]
			labels_dict[i.value]=i.type
		'''if i.type == 'CLASS_DEF':
			#i.value = tokens[j].value #Metemos como valor en el token parallel, la funcion parallel
			#labels_dict[i.value]=i.type
			if dir!="":
				i.value = dir+"."+file+"."+i.value.split("(")[0]
			else:
				if i.value.split("(")[0] == 'main':
					i.value = file+"."+i.value.split("(")[0]
				else:
					i.value = file+"."+i.value.split("(")[0]
			labels_dict[i.value]=i.type'''

def getClasses(filename):
	token_list = []
	lexer = lex.lex()
	class_dict = {}

	with open(filename,'r') as fi:
	    
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
	            if tok.type == 'CLASS_DEF':
	            	class_dict[tok.value]= ""
	            	token_list.append(tok)

	for i in token_list:
		print("PARA EL TOKEN",i)
		fi = open(filename,'r')
		for j,line in enumerate(fi,1):
			if j >= i.lineno:
				#class_dict[i.value] += line
				if line.count('\t') == 0:
					print("Termino de escribir")
					break
				if line.count('\t') != 0:
					class_dict[i.value] += line
				
			continue

	return class_dict