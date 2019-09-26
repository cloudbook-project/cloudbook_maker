from __future__ import print_function
import ast
import re
import os

def du_name_assignation(con, function_list, du_list):
	'''This function gets function list and assign the first function du name to the final du with the group of functions'''
	print(">>Enter in du_name assignation")
	cursor = con.cursor()
	if type(function_list)!=list:#In case there is only one function
		function_list = function_list.split() #convert string to list with strings

	#du number select
	query="SELECT DU from FUNCTIONS where ORIG_NAME=="+"'"+function_list[0]+"'"
	cursor.execute(query)
	du_number = cursor.fetchone()[0]
	du_name = "du_"+str(du_number)#(cursor.fetchone()[0])
	print("\tThe du_name will be: ", du_name)
	while du_name in du_list: #check until there is no repeated number
		du_number += 1
		du_name = "du_"+str(du_number)
	print(">>Exit from du_name assignation")
	return du_name

def get_final_imports(con, function_list):
	'''This function gets imports from original source code and unifies in final imports list for the actual du
	For everye function in the du:
		extract module name
			with module name, extract imports from sqlite'''
	print(">>Enter in get final imports")
	print(function_list)
	if isinstance(function_list, list) == False:
		function_list = function_list.split()
	final_imports = []
	cursor = con.cursor()
	for i in function_list:
		module_name = i[:i.rfind('.')] #extraer su nombre de modulo original
		#print ("\t\tmodule_name de",i,"es",module_name)
		query = "SELECT FINAL_IMPORTS from MODULES where ORIG_NAME=="+"'"+module_name+"'"
		print(query)
		cursor.execute(query)
		#translate unicode to list of strings
		for n in cursor.fetchone():
			try:
				sub_list = ast.literal_eval(n)
				final_imports.extend(sub_list) #extends the list, not append
			except ValueError:
				final_imports.append(str(n))
	final_imports = list(set(final_imports)) #remove duplicates
	#remove auto_import
	final_imports_aux = []
	for i,elem in enumerate(final_imports):
		if elem.find("du_") != -1: #dont copy import du
			pass
		else:
			final_imports_aux.append(elem)

	final_imports = final_imports_aux
	if "import threading" not in final_imports:
		final_imports.append("import threading")
		final_imports.append("from threading import Lock")
		final_imports.append("import time")
	if "import json" not in final_imports:
		final_imports.append("import json")
	if "import sys" not in final_imports:
		final_imports.append("import sys")
	print ("\t\tFinal Imports: ", final_imports, "\n")
	print(">>Exit from get final imports")
	return final_imports

def get_final_name(con, orig_name):
	cursor = con.cursor()
	query = "SELECT FINAL_NAME from FUNCTIONS where ORIG_NAME = '"+orig_name+"'"
	cursor.execute(query)
	final_name = cursor.fetchone()[0]
	return final_name

def translate_invocation(con,orig_module,orig_function_name,invoked_function,function_list,file_descriptor,du_name,line,tabs,invoker_name,nonblocking_invocation,config_dict):
	#El proceso de traduccion consiste en:
			#si la funcion esta en la misma du(estara en la function list) se invoca sin nombre de modulo
			#else invoke("du_xx.f(...)"), la du_xx la sacamos de la tabla de funciones
	c = con.cursor()
	newline = ""
	#nombrefuncompleto es como esta en la base de datos,con _VAR_ si es vble global
	old_function = invoked_function #modulo.nombrefuncompleto
	aux_function = old_function #modulo.nombrefuncomplet
	old_function = old_function.split(".")[-1] #solo nombrefuncompleto
	parallel_fun = False #Marcador que sirve para tratar bien las variables en las invocaciones a funcion parallel
	recursive_fun = False
	local_fun = False
	#c.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME like '%"+invoked_function+"%'")
	c.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+invoked_function+"'")
	row = c.fetchone()
	invoked_du = row[0]
	invoked_function = row[1]
	print("\t\t\t\tPREfuncion, du invocada:",invoked_function,invoked_du)
	#get final name of invoker
	c.execute("SELECT FINAL_NAME from functions where ORIG_NAME = '"+orig_module+"."+invoker_name+"'")
	row = c.fetchone()
	invoker_name = row[0]
	#Aqui si old_function esta en dict labels, la invoked du sera 10000
	print("\t\t\t\taux_function: ", aux_function, " y invocation_function: ", invoked_function)
	print("\t\t\t\torig_function_name: ", orig_function_name)
	if aux_function in config_dict["labels"]:
		if config_dict["labels"][aux_function] == "PARALLEL":
			invoked_du=10000
			parallel_fun = True
		if config_dict["labels"][aux_function] == "RECURSIVE":
			invoked_du=5000
			invoked_function = "recursive_"+invoked_function
			recursive_fun = True
		if config_dict["labels"][aux_function] == "LOCAL":
			print("\t\t\t\t ES LOCAALL")
			invoked_du = du_name
			local_fun = True
	if str(invoked_du) in du_name:#La invocacion es local
	##TODOO hay q ciomprobar si es parallel, en cuyo caso se invoca como remota, con du_10000
		#invoked_function = invoked_function[invoked_function.rfind(".")+1:len(invoked_function)]
		#newline = invoked_function+"()"
		if "_VAR_" in old_function: #si es global var
			print("\t\t\t\t\tEs una variable global local")
			old_function = old_function.replace("_VAR_","")
			#newline = line.replace(old_function,invoked_function+"."+old_function)
			#newline = re.sub(r'\s*',"",newline)
			variables = line
			variables = re.sub(r'\s*',"",variables)
			if old_function in variables:
				print("\t\t\t\t\t\told function es",old_function,"invoked_function es", invoked_function)
				variables = variables.replace(old_function,invoked_function+"."+old_function)
				if "=" in variables:
					variables_aux = variables.split("=")
					variable_aux = variables.split("=")[-1]
					variables = variables.replace(variable_aux,"")
					##variables = variables.replace("=","%3d")
					##newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+'"'+invoked_function+"."+variables+"'+str("+variable_aux+")"+"+' \", '+"+"str(ver_"+old_function+"))#[0]"
					newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+'"'+variables+"'+str("+variable_aux+")"+"+' \", '+"+"str(ver_"+old_function+"))#[0]"
					#add invoker in call
					newline_aux = newline.rsplit(")",1)
					newline = newline_aux[0] + ",'"+invoker_name+"')"+newline_aux[1].replace(")","")
				else:
					if "(" in variables:#Hay un parametro que tengo que conservar como el original y stringuearlo TODO: Creo que nunca caigo aqui el str fallaria porque no tengo parentesis
						variables_aux=""
						variable_aux = ""
						ind_aux = variables.find("(") # indice, porque puede haber varios parentesis (si usas una tupla por ejemplo)
						variable_aux = variables[ind_aux:len(variables)]#"("+variables.split("(")[-1]
						variables = variables.replace(variable_aux,"")
						#variables = variables + "('+str"+variable_aux+"')" #Antes de la depuracion de nbody4, y poner siempre la version 0
						#variables = variables + "('+str"+variable_aux+"+')" #En caso de invocacion local sin llamar a "invoker"
						variables = '"'+variables + "('+str"+variable_aux+"+')"+'"' #preparado para meterlo dentro de un "invoker"
						##newline = invoked_function+"('"+variables+"', str(0))#" #En caso de invocacion local sin llamar a "invoker"
						newline = "invoker(['du_"+str(invoked_du)+"'],'"+invoked_function+"','"+variables+",'+str(0),'"+invoker_name+"')#" #preparado para meterlo dentro de un "invoker"
					else:#only the actualization of global var like globalvar = globalvar_aux it has "=" and no "("
						variables_aux = ""
						variable_aux = ""
						ind_aux = variables.find("=")+1
						variable_aux = variables[ind_aux:len(variables)]#the right part of =
						variables = variables.replace(variable_aux,"")
						##variables = variables + "'+str("+variable_aux+")" #En caso de invocacion local sin llamar a "invoker"
						variables = '"'+variables + "('+str"+variable_aux+"+')"+'"' #preparado para meterlo dentro de un "invoker"
						##newline = invoked_function+"('"+variables+", str(0))#" #En caso de invocacion local sin llamar a "invoker"
						newline = "invoker(['du_"+str(invoked_du)+"'],'"+invoked_function+"','"+variables+",'+str(0),'"+invoker_name+"')#" #preparado para meterlo dentro de un "invoker"
				#newline = invoked_function+"('"+variables+"', str(ver_"+old_function+"))#"
				#newline = invoked_function+"('"+variables+"', str(0))#"
				
		else: #es una fun normal
			print("\t\t\t\tLOCAAALLLLL", invoked_function, old_function)

			newline = line.replace(old_function,invoked_function)
			newline = re.sub(r'\s*',"",newline)
			if line.find("(")!=-1: #si no tiene parentesis en global var
				variables = line.split("(")[1]
			else:
				variables=""
			##Translate vars SOLO SI TRADUCIMOS POR INVOKER TODO: Que pasa si variables aux 2 es ""
			variables2 = line
			variables2 = re.sub(r'\s*',"",variables2)
			if variables2.find("(")!=-1:
				variables2 = variables2.split("(")[-1]
				variables2 = variables2.replace(")","")
				#tostring every var
				variables2_aux = ""
				for i in variables2.split(","):
					if variables2_aux == "":
						variables2_aux = variables2_aux+"str("+i+")"
					else:
						variables2_aux = variables2_aux+"+','+ str("+i+")"
			##Transalted vars
			if local_fun == True:
				##newline = invoked_function + "("+ variables  #Para invocacion normal sin "invoker"
				#variables2 = '"'+variables2 + "('+str"+variables2_aux+"+')"+'"' #preparado para meterlo dentro de un "invoker"
				if invoked_du.find("du_") != -1:
					invoked_du = invoked_du.replace("du_","")
				newline = "invoker(['du_"+str(invoked_du)+"'],'"+invoked_function+"',"+variables2_aux+",'"+invoker_name+"')#" #preparado para meterlo dentro de un "invoker"
				local_fun = False
				if nonblocking_invocation:
					newline = newline.replace(invoked_function,"nonblocking"+invoked_function)
			else:
				##newline = "json.loads("+invoked_function + "("+ variables + ")"#PAra invocacion local normal
				print("Traceando",invoked_du)
				try:
					if invoked_du.find("du_") != -1:
						invoked_du = invoked_du.replace("du_","")
				except:
					invoked_du=invoked_du
				newline = "json.loads(invoker(['du_"+str(invoked_du)+"'],'"+invoked_function+"',"+variables2_aux+",'"+invoker_name+"'))#" #preparado para meterlo dentro de un "invoker"
			newline = re.sub(r'\s*',"",newline)
	else:#La invocacion es externa
		#invoked_function = invoked_function[invoked_function.rfind("."):len(invoked_function)]
		#newline = "invoke('du_"+str(invoked_du)+"' , '"+invoked_function+"()')"
		#newline = "invoker('du_"+str(invoked_du)+"."+invoked_function+"()')"
		#invoker(['''+"'du_"+str(global_fun_du)+"'"+'''],'''+"'"+global_fun_name+"'"+''',"'None',"+str('''+fun_name+'''.ver_'''+globalName+'''))
		variables = ""
		if "_VAR_" not in old_function and parallel_fun==False:#Si no es global var
			#
			variables = line
			variables = re.sub(r'\s*',"",variables)
			if variables.find("(")!=-1:
				variables = variables.split("(")[-1]
				variables = variables.replace(")","")
				#tostring every var
				variables_aux = ""
				for i in variables.split(","):
					if variables_aux == "":
						variables_aux = variables_aux+"str("+i+")"
					else:
						variables_aux = variables_aux+"+','+ str("+i+")"
			newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"',"+variables_aux+")"
			newline_aux = newline.rsplit(")",1)
			newline = newline_aux[0] + ",'"+invoker_name+"')"+newline_aux[1].replace(")","")
		if "_VAR_" in old_function and parallel_fun==False:#Si es una variable global hay que sacar los parametros de la llamada.
		#si es una llamada a una funcion, hay que sacar la linea y lo que hay entre parentesis TODO
		#si es una asignacion, hay que copiar la linea como la variable entera
			old_function = old_function.replace("_VAR_","")
			variables = line
			variables = re.sub(r'\s*',"",variables)
			#Aqui miro las variables y las trato segun lo que haya: por ahora '=' o '.' y '()'
			variables_aux=""
			variable_aux = ""
			if "=" in variables:
				variables_aux = variables.split("=")
				variable_aux = variables.split("=")[-1]
				variables = variables.replace(variable_aux,"")
				variables = variables.replace("=","%3d")
				newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+'"'+invoked_function+"."+variables+"'+str("+variable_aux+")"+"+' \", '+"+"str(ver_"+old_function+"))#[0]"
				#add invoker in call
				newline_aux = newline.rsplit(")",1)
				newline = newline_aux[0] + ",'"+invoker_name+"')"+newline_aux[1].replace(")","")
			else:
				if "(" in variables:
					#bla bla bla
					#variables_aux = variables.split("(")
					ind_aux = variables.find("(") # indice, porque puede haber varios parentesis (si usas una tupla por ejemplo)
					variable_aux = variables[ind_aux:len(variables)]#"("+variables.split("(")[-1]
					variables = variables.replace(variable_aux,"")
					#newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+'"'+invoked_function+"."+variables+"('+str"+variable_aux+"+')\"'"+"+' , '+"+"str(ver_"+old_function+"))"
					newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+'"'+invoked_function+"."+variables+"('+str"+variable_aux+"+')\"'"+"+' , '+"+"str(0))"
					#add invoker in call
					newline_aux = newline.rsplit(")",1)
					newline = newline_aux[0] + ",'"+invoker_name+"')"+newline_aux[1].replace(")","")
				else:
					#newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"."+old_function+"','"+invoked_function+"."+variables+"')[0]"
					newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+invoked_function+"."+variables+"')[0]"
					#add invoker in call
					newline_aux = newline.rsplit(")",1)
					newline = newline_aux[0] + ",'"+invoker_name+"')"+newline_aux[1].replace(")","")
		#Pongo el campo 0, porque en las operaciones de cambio, solo queremos el nuevo valor, la version no se pide nunca en el codigo
		if parallel_fun == True:
			#TODO tratar el _VAR_ aqui tambien, por si se hace una global var parallel por algun casual
			variables = line
			variables = re.sub(r'\s*',"",variables)
			parallel_fun = False
			if variables.find("(")!=-1:
				variables = variables.split("(")[-1]
				variables = variables.replace(")","")
				#tostring every var
				variables_aux = ""
				for i in variables.split(","):
					if variables_aux == "":
						variables_aux = variables_aux+"str("+i+")"
					else:
						variables_aux = variables_aux+"+','+ str("+i+")"
			#invoker(['du_0'], 'cloudbook_th_counter',"'++'")#Para hacer el sync
			pre_line = '''invoker(['du_0'], 'cloudbook_th_counter',"'++'")
'''
			newline = pre_line+"\t"*tabs+"invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"',"+variables_aux+")"
			#add invoker in call
			newline_aux = newline.rsplit(")",1)
			newline = newline_aux[0] + ",'"+invoker_name+"')"+newline_aux[1].replace(")","")
			#podria omitir el campo 0 aqui
			#Pongo el campo 0, porque en las operaciones de cambio, solo queremos el nuevo valor, la version no se pide nunca en el codigo
		#Si es funcion normal:
		#newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+invoked_function+"."+variables+"')[0]"
		
	print("\t\t\t\tPOST:funcion, du invocada:",invoked_function,invoked_du)
	return newline

def writeGlobalCode(fun_name,fo, globalName,module ,con, config_dict, tabs):
	'''Escribimos el codigo de invocacion para las variables globales. 
	fun_name: la funcion en la q estamos
	global_name: la variable global
	global_fun_name: el nombre de la funcion global tal como esta en la tabla final name'''
	#Get final name from original global fun name, sera necesario _VAR_+globalName
	#Tambien me hace falta la du, porque las llamadas seran invoker
	#Hay que coger tambien el final name de fun_name, porque ese va a ser el que denomine a los atributos de la funcion: f0.body_list
	# 	tener en cuenta si la funcion es paralela, porque habra que escribir parallel_final_fun_name
	tabulations = ""#tabulations vacio, porque ya meto yo una tabulacion siempre
	if tabs > 1:
		for i in range(tabs-1):
			tabulations+="\t"
	fun_name = fun_name.split(" ")[1]
	cursor = con.cursor()
	print ("\t\t\t\tSELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+module+"._VAR_"+globalName+"'")
	cursor.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+module+"._VAR_"+globalName+"'")
	row = cursor.fetchone()
	global_fun_du = row[0]
	global_fun_name = row[1]
	#pillo el final name para que los atributos se llamen de forma correcta
	cursor.execute("SELECT FINAL_NAME from functions where ORIG_NAME = '"+module+"."+fun_name+"'")
	row = cursor.fetchone()
	final_fun_name = row[0]
	#get invoker_name
	cursor.execute("SELECT FINAL_NAME from functions where ORIG_NAME = '"+module+"."+fun_name+"'")
	row = cursor.fetchone()
	fun_name = row[0]
	if (module+"."+fun_name) in config_dict["labels"]:#Aniado parallel si es el codigo de la funcion parallel
		if config_dict["labels"][module+"."+fun_name] == 'PARALLEL':
			final_fun_name = "parallel_"+final_fun_name
	#print "\t\t Empezamos a escribir el codigo de la variable global"
	fo.write("#Automated code for global var:\n #fun_name: "+ fun_name+" final fun name: "+final_fun_name+" globalName: "+ globalName+ " destiny du: "+ str(global_fun_du)+" global_fun_name: "+ global_fun_name+"\n")
	#fo.write("#Automated code for global var:\n #fun_name: "+ fun_name+" globalName: "+ globalName+ " destiny du: "+ str(global_fun_du)+" global_fun_name: "+ global_fun_name+"\n")

	fo.write('''#============================global vars automatic code=========================
	#'''+globalName+'''
	'''+tabulations+'''if not hasattr('''+final_fun_name+''', "'''+globalName+'''"):
		'''+tabulations+final_fun_name+'''.'''+globalName+''' = None

	'''+tabulations+'''if not hasattr('''+final_fun_name+''', "ver_'''+globalName+'''"):
		'''+tabulations+final_fun_name+'''.ver_'''+globalName+''' = 0
        
	'''+tabulations+'''aux_'''+globalName+''',aux_ver = invoker(['''+"'du_"+str(global_fun_du)+"'"+'''],'''+"'"+global_fun_name+"'"+''',"'None',"+str('''+final_fun_name+'''.ver_'''+globalName+''')'''+",'"+fun_name+"'"+''')
	'''+tabulations+'''if aux_'''+globalName+''' != "None":
		'''+tabulations+final_fun_name+'''.'''+globalName+''' = aux_'''+globalName+'''
	'''+tabulations+globalName+"="+final_fun_name+"."+globalName+'''
	'''+tabulations+final_fun_name+'''.ver_'''+globalName+"= aux_ver"'''
	'''+tabulations+''''''+"ver_"+globalName+"= "+final_fun_name+'''.ver_'''+globalName+'''
		''')

	return "hola"

def writeGlobalDef(fun_name, final_name, gl_value, fo, con):
	'''Aqui va el codigo de la definicion de las variables globales'''

	fo.write('''def '''+final_name+'''(op, old_ver):
	if not hasattr('''+final_name+''', "'''+fun_name+'''"):
		'''+final_name+'''.'''+fun_name+'''='''+str(gl_value)+'''
	if not hasattr('''+final_name+''', "ver_'''+fun_name+'''"):
		'''+final_name+'''.ver_'''+fun_name+'''= 1
	if not hasattr('''+final_name+''', "lock_'''+fun_name+'''"):
		'''+final_name+'''.lock_'''+fun_name+''' = threading.Lock()
	if op == "None":
		if old_ver == '''+final_name+'''.ver_'''+fun_name+''':
			return json.dumps(("None", old_ver))
		else:
			try:
				return json.dumps(('''+final_name+'''.'''+fun_name+''','''+final_name+'''.ver_'''+fun_name+''')) 
			except:
				return json.dumps(('''+'''str('''+final_name+'''.'''+fun_name+'''),'''+final_name+'''.ver_'''+fun_name+'''))
	else:
		try:
			'''+final_name+'''.ver_'''+fun_name+'''+=1
			return json.dumps((eval(op),'''+final_name+'''.ver_'''+fun_name+'''))
		except:
			with '''+final_name+".lock_"+fun_name+''':
				exec(op)
				'''+final_name+'''.ver_'''+fun_name+'''+=1
			return json.dumps(("done",'''+final_name+'''.ver_'''+fun_name+'''))''')

def write_nonblocking_invocation((complete_name,line),fo,con):
	function_orig_name = complete_name[complete_name.rfind(".")+1:]
	#clean line
	line = re.sub(r'\s*',"",line)
	#get final_name
	c = con.cursor()
	c.execute("SELECT FINAL_NAME from functions where ORIG_NAME = '"+complete_name+"'")
	row = c.fetchone()
	function_final_name = row[0]
	#get params in appropiate format for creating a python thread
	params = line.split(function_orig_name)[-1]
	orig_params = params
	params = params[1:-1]
	params = "["+params+"]"
	#write threading code
	fo.write("def nonblocking"+function_final_name+orig_params+":\n")
	fo.write('''	thread'''+function_final_name+''' = threading.Thread(target='''+function_final_name+''', daemon = False, args = '''+params+''')
	thread'''+function_final_name+'''.start()
	return json.dumps("thread launched")

''')