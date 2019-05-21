#create the deployable units
import ast #for translating unicode strings
import re
import os

def create_dus(config_dict):
	con=config_dict["con"]
	matrix=config_dict["matrix_filled"]
	input_path=config_dict["input_dir"]
	output_path=config_dict["output_dir"]

	print "dus: ",range(1,len(matrix[0]))
	du_list =[]
	for i in range(1,len(matrix[0])):
		du_list.append(create_du(con,matrix[0][i],input_path,output_path, config_dict))
	return du_list


def create_du(con,function_list,input_path,output_path, config_dict):
	print "\t============== create du ==============="
	#look in functions table for the first funtion name that matches with function_list[0]
	#this row UD will be the name of this deployable unit and it will contains all function from function_list
	print "\tFunction list:", function_list
	#en las du de una sola funcion, no viene en forma de lista la function list, si no como un string con la funcion
	pragmas = ["__CLOUDBOOK:PARALLEL__","SYNC"]
	#ud guide: 1
	cursor = con.cursor()
	if type(function_list)!=list: 
		aux_funlist = []
		aux_funlist.append(function_list)
		function_list = aux_funlist

	cursor.execute("SELECT DU from FUNCTIONS where ORIG_NAME=="+"'"+function_list[0]+"'")
	du_name = "du_"+str(cursor.fetchone()[0])
	print "\tVa a ser la du: ", du_name

	#para cada elemento j, de function_list: 
		#extraer su nombre de modulo original
		#entrar en la tabla modules y coger los imports traducidos, y guardarlos en un lista de imports finales sin repeticion
		#eliminar de la lista si existiese, el import de la ud que estamos creando
	#ud guide: 2
	final_imports = []
	for i in function_list:
		module_name = i[:i.rfind('.')] #extraer su nombre de modulo original
		print "\t\tmodule_name de",i,"es",module_name 
		cursor.execute("SELECT FINAL_IMPORTS from MODULES where ORIG_NAME=="+"'"+module_name+"'")
		#translate unicode to list of strings
		for n in cursor.fetchone():
			#print "\tImports en la bbdd:",n
			try:
				sub_list = ast.literal_eval(n)
				final_imports.extend(sub_list)
			except ValueError:
				final_imports.append(str(n))
	final_imports = list(set(final_imports)) #remove duplicates
	#remove auto_import
	final_imports_aux = []
	for i,elem in enumerate(final_imports):
		#print "\telem= ",elem
		if elem.find("du_") != -1:
			#print "\timport du en la poscion ",i, ":", elem
			#final_imports.remove(elem)
			#print f\tinal_imports
			pass
		else:
			final_imports_aux.append(elem)

	final_imports = final_imports_aux
	if "import threading" not in final_imports:#PARALLEL: Para poder hacer threads si hay funciones parallel
		final_imports.append("import threading")
		final_imports.append("from threading import Lock")
	final_imports.append("import sys")#TODO comprobar que no este repetido
	print "\t\tFinal Imports: ", final_imports, "\n"		


	#create ud file and open it for write
	#escribir en el fichero la lista de imports finales, excepto 
	#for each function name in function_list:
		#enter in original file, copy the function text,
		#analizar el texto y buscar la primera funcion de la tabla de funciones, en caso de encontrarla
		#se traduce, despues se hace lo mismo con la segunda fun de la tabla de funciones, y asi hasta el final
		#El proceso de traduccion consiste en(se puede hacer en translate invocation):
			#ver translate_invocation()
		#after translation of invocations of function text, include it into the du file
	#ud guide: 3
	#ud guide: 3.1
	cursor = con.cursor()
	output_file = output_path+os.sep+du_name+".py"
	fo = open(output_file, 'w')
	for i in final_imports:
		fo.write(i)
		fo.write("\n")
	fo.write("\n")
	fo.write("invoker=None\n\n")

	#ud guide: 3.2
	for i in function_list:
		#ud guide: 3.2.1
		print "\tPara la funcion "+i
		aux_ind = i.rfind('.')
		module = i[:i.rfind('.')]
		name = i[i.rfind('.'):len(i)]
		name = name[1:len(name)]
		cursor.execute("SELECT FINAL_NAME from FUNCTIONS where ORIG_NAME = '"+i+"'")
		final_name = cursor.fetchone()[0]
		#print "\tmodule, name: ",module, name
		#print "\tinput path: ",input_path
		#ud guide: 3.2.2
		input_file = input_path+os.sep+module.replace('.',os.sep)+".py"
		print "\tAbrimos el fichero: "+ input_file
		fi = open(input_file,'r')
		isfun=False
		for i,line in enumerate(fi,1):
			#ud guide: 3.2.2.1
			#print "\t\tMiramos la linea "+ line
			translated_fun = False
			tabs = 0
			tabs += line.count('\t')
			linea = line.split()
			#Ignoramos comentarios
			#si linea es comentario, la ignoro si no es un pragma BLOQUEADO POR AHORA
			#if "#" in line and line not in pragmas:
				#continue
			#Adaptamos o incorporamos a nombre funcion, a def loquesea o declaracion de variable global
			#ud guide: 3.2.2.2
			if "_VAR_" in name:
				fun_name = name.replace("_VAR_","")
			else:
				fun_name = "def " + name
			###Translate prints
			#ud guide: 3.2.2.3
			newprint = ""
			newvar = ""
			if "print " + '"@' in line:
				print "AQUI PRINT"
				line_aux = line.split("@",1)
				print line_aux[1]
				arg_aux = '"'+line_aux[1].rstrip()
				#arg_aux = "eval("+arg_aux+")"
				arg_aux = arg_aux
				print "Argumento Llamada", arg_aux
				
				for i in range(tabs):
					newprint = "\t"+newprint
					newvar = "\t"+newvar
				if du_name == "du_0":
					newvar = newvar + "cloudbook_txt = " + arg_aux + "\n"
					newprint = newprint + 'cloudbook_print(\"\'\"+'+"cloudbook_txt+"+"\"\'\""+")"
					line = newvar+ "\n" + newprint+"\n"
				else:
					#arg_aux = "'"+arg_aux+"'"
					newvar = newvar + "cloudbook_txt = " + arg_aux + "\n" 
					newprint = newprint + 'invoker("du_0.cloudbook_print(\'\"+'+"cloudbook_txt+\"\')\""+")"
					line = newvar+ "\n" + newprint+"\n"
			###Three kinds of fun in file
			#ud guide: 3.2.2.4
			if (fun_name in line) and (tabs==0):
				print "\t\tHemos encontrado la funcion: ", name, " que sera ", final_name
				if "_VAR_" in name:
					#fo.write(line.replace(fun_name,final_name+" con el valor"))#CODIGO DE FUNCION DE VARIABLE GLOBAL
					#Valor de la variable global
					gl_value = line.split("=")[1]
					#t.value = re.sub(r'\s*',"",t.value)
					gl_value = re.sub(r'\s*',"",gl_value)
					line3 = writeGlobalDef(fun_name, final_name, gl_value, fo, con)
					continue
				else:
					#Si es Parallel escribo nombre y codigo de hilos, y nuevo nombre,
					#a continuacion sigo escribiendo igual
					if module+"."+name in config_dict["labels"]:
						if config_dict["labels"][module+"."+name] == 'PARALLEL':
							funvariables = line[line.find("("):len(line)-2]#el -2 para quitar el ":" final y el \n
							print funvariables
							fo.write(line.replace(name, final_name))#original fun name
							#write thread code 
							'''print("Esto es una prueba NONBLOCKING soy el fichero B")
							hilo1 = threading.Thread(target=blockingB, daemon = False)
							hilo1.start()
							return "Ya he llamado"'''
							funvariables=funvariables.replace("(","[")
							funvariables=funvariables.replace(")","]")
							fo.write('''	thread'''+final_name+''' = threading.Thread(target= parallel_'''+final_name+''', daemon = False, args = '''+funvariables+''')
	thread'''+final_name+'''.start()
	return json.dumps("thread launched")

''')
							final_name = "parallel_"+final_name						

					fo.write(line.replace(name, final_name))
				isfun = True
			#ud guide: 3.2.2.5
			if (fun_name not in line) and (isfun):
				print "\t\tMiramos dentro de la funcion"
				if "print" in line:
					fo.write(line)
					continue
				if "global" in line:
					line2 = "#"+ line + "#Aqui va el chorrazo de codigo"
					globalName = line.split(" ")[1]
					#globalName = globalName.replace("\n","")
					globalName = re.sub(r'\s*',"",globalName)
					line3 = writeGlobalCode(fun_name, fo, globalName,module, con, config_dict, tabs)
					#print line3
					fo.write(line2.replace("\n","")+"\n")
					continue
				if "#SYNC" in line:
					if line.find(":") != -1:
						time = line.split(":")[1]
						time = time.replace(":","")
						time = int(time)/10
						time = str(time)
					#line = line.replace("#SYNC",'''while json.loads(cloudbook_th_counter("")) > 0: #This was sync
			#sleep(0.01)
			#''')
					#todo: Los tabs bien
						line = "\t"*tabs+'''temp = 0
		while json.loads(cloudbook_th_counter("")) > 0: #This was sync
			if temp > '''+time+''':
				print("threading failure")
				sys.exit()
			sleep(0.01)
			temp+=1
'''
					else:
						line = "\t"*tabs+'''while json.loads(cloudbook_th_counter("")) > 0: #This was sync
			sleep(0.01)
'''
					fo.write(line)
					continue
				#Hay que ver si dentro de la funcion, se llama a alguna otra funcion de la tabla functions
				#hago una query de los orignames y los guardo en una lista
				cursor.execute("SELECT ORIG_NAME from FUNCTIONS")
				row = cursor.fetchall()
				orig_list = [] #list of orignames
				for j in row:
					orig_fun_name = j[0]
					trunc = orig_fun_name.rfind(".")+1
					orig_fun_name = orig_fun_name[trunc:len(orig_fun_name)]
					if "_VAR_" in orig_fun_name.encode('ascii'):#Casi distinto en global vars functions
						orig_list.append((j[0].encode('ascii'),orig_fun_name.encode('ascii').replace("_VAR_","")))#tuplas(nombreorig,solofun)
					else:
						orig_list.append((j[0].encode('ascii'),orig_fun_name.encode('ascii')))#tuplas(nombreorig,solofun)
				print "\t\t\tBuscamos estas: ", orig_list
				#miro si la fun (segunda parte de la tupla) esta en line
				for j in orig_list:
					if j[1] in line:#nombre solo fun
						print "\t\t\tEncuentro esta: ", j[1], " aqui", i, ": ", line
						#reconocer la invocacion en la linea
						aux_line = line
						invocation_index = 0#to do, usarlo para escribir bien la linea, solo traducir la invocacion
						aux_line = aux_line.split()
						print "\t\t\tEsta escrita asi", aux_line
						for i,elem in enumerate(aux_line):
							if j[1] in elem:
								aux_line = aux_line[i]
								invocation_index = i

						invocation_fun = aux_line
						print "INVOCATION FUN========================================"+invocation_fun
						if "_VAR_" in j[0]:#Es una variable global solo tocamos modificaciones, con parentesis
							if invocation_fun.find("(")!=-1:
								invocation_fun = "_VAR_"+invocation_fun[:invocation_fun.rfind("(")]
								if invocation_fun.find(".")!=-1:
									invocation_fun = invocation_fun.split(".")[0]
							elif ("=" in line) and (invocation_index==0): #TODO es una asignacion y hay que traducirla
							#elif ("=" in line):#TODO_ACT estudiar y hacer que se haga bien esto
							#Tiene que estar antes del igual
								invocation_fun = "_VAR_"+invocation_fun
							else:
								continue
							#else:# No tiene parentesis
							#	invocation_fun = "_VAR_"+invocation_fun
							#if invocation_fun.find(".")!=-1:
								#invocation_fun = invocation_fun.split(".")[0]
							#if invocation_fun.find(":")!=-1:#Hacer esto para todos los elementos raros
							#	invocation_fun = invocation_fun.replace(":","")
						else:
							invocation_fun = invocation_fun[:invocation_fun.rfind("(")]
						print "\t\t\tLa invocacion que buscamos es", invocation_fun, " y en FUNCTIONS es ", j[0]
						if j[0] == invocation_fun:
							print "\t\t\tEsta bien escrita"
							complete_name = invocation_fun
						else:
							#Esto es solo si el modulo tiene un punto, si no, peta
							if module.rfind('.')!=-1:							
								complete_name = module[:module.rfind('.')+1]+invocation_fun
							else:
								complete_name = module+'.'+invocation_fun
							print "\t\t\tCompletamos nombre y queda: ", complete_name
						new_line = translate_invocation(con,module,fun_name,complete_name,function_list,fo,du_name,line,tabs,config_dict)
						#escribimos la newline dentro de su linea probar poniendo una linea completa
						aux_line2 = line.split()
						aux_line2[invocation_index] = new_line
						#new_line = str(aux_line2)
						new_line = ""
						for k,elem in enumerate(aux_line2):
							if k == 0: 
								new_line = aux_line2[k]
							else:
								new_line = new_line + " " + aux_line2[k]
						#new_line = new_line.replace(" ","")
						#print "LINEA: ",aux_line2
						#for k,elem in enumerate(aux_line2):
						#	if k < invocation_index:
						#		new_line = elem + " " + new_line
						#	if k > invocation_index:
						#		new_line = new_line + " " + elem
						for i in range(tabs):
							new_line = "\t"+new_line
						fo.write(new_line)
						fo.write("\n")
						translated_fun = True
				if "return" in line:
					print "AQUI RETURN"
					aux_ret = line.split()[-1]
					line = line.replace(aux_ret,"json.dumps("+aux_ret+")")
				if translated_fun==False:
						fo.write(line)

			#ud guide: 3.2.2.6
			if (fun_name not in line) and (tabs==0):
				#Hara falta traducir aqui
				isfun = False
		#ud guide: 3.2.3
		if "parallel_" in final_name:#Before return, sychronize thread
			#pre_line = '''invoker(['du_0'], 'cloudbook_th_counter',"'--'")
			#''' 
			fo.write("\n\tinvoker(['du_0'], 'cloudbook_th_counter',\"'--'\")\n")
		#ud guide: 3.2.4
		fo.write("\n\treturn json.dumps('cloudbook: done') \n\n")					
	#ud guide: 3.3
	fi.close()
	if (du_name == "du_0"):
		fo.write('''def cloudbook_print(element):
	print (element)
	return "cloudbook: done"
	
''')
		fo.write('''def cloudbook_th_counter(value):
	if not hasattr(cloudbook_th_counter, "val"):
		cloudbook_th_counter.val = 0
	if not hasattr(cloudbook_th_counter, "cerrojo"):
		cloudbook_th_counter.cerrojo = Lock()
	if value == "++":
		with cloudbook_th_counter.cerrojo:
			cloudbook_th_counter.val += 1
	if value == "--":
		with cloudbook_th_counter.cerrojo:
			cloudbook_th_counter.val -= 1
	return json.dumps(val)

''')
		fo.write('''def main():
	#f0()
	#return "cloudbook: done"
	return f0()

''')

		fo.write('''if __name__ == '__main__':
	f0()
			''')
	fo.close()
	return du_name


def translate_invocation(con,orig_module,orig_function_name,invoked_function,function_list,file_descriptor,du_name,line,tabs,config_dict):
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
	#c.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME like '%"+invoked_function+"%'")
	c.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+invoked_function+"'")
	row = c.fetchone()
	invoked_du = row[0]
	invoked_function = row[1]
	print("PREfuncion, du invocada:",invoked_function,invoked_du)
	#Aqui si old_function esta en dict labels, la invoked du sera 10000
	print("aux_function: ", aux_function, " y invocation_function: ", invoked_function)
	if aux_function in config_dict["labels"]:
		if config_dict["labels"][aux_function] == "PARALLEL":
			invoked_du=10000
			parallel_fun = True
	if str(invoked_du) in du_name:#La invocacion es local
	##TODOO hay q ciomprobar si es parallel, en cuyo caso se invoca como remota, con du_10000
		#invoked_function = invoked_function[invoked_function.rfind(".")+1:len(invoked_function)]
		#newline = invoked_function+"()"
		if "_VAR_" in old_function: #si es global var
			old_function = old_function.replace("_VAR_","")
			#newline = line.replace(old_function,invoked_function+"."+old_function)
			#newline = re.sub(r'\s*',"",newline)
			variables = line
			variables = re.sub(r'\s*',"",variables)
			if old_function in variables:
				variables = variables.replace(old_function,invoked_function+"."+old_function)
				if "(" in variables:#Hay un parametro que tengo que conservar como el original y stringuearlo
					variables_aux=""
					variable_aux = ""
					ind_aux = variables.find("(") # indice, porque puede haber varios parentesis (si usas una tupla por ejemplo)
					variable_aux = variables[ind_aux:len(variables)]#"("+variables.split("(")[-1]
					variables = variables.replace(variable_aux,"")
					#variables = variables + "('+str"+variable_aux+"')" #Antes de la depuracion de nbody4
					variables = variables + "('+str"+variable_aux+"+')"
			#newline = invoked_function+"('"+variables+"',"+"ver_"+old_function+")" #Antes de la depuracion de nbody4
			newline = invoked_function+"('"+variables+"', str(ver_"+old_function+"))#"
			#newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"."+old_function+"','"+invoked_function+"."+variables+"')[0]"
		else: #es una fun normal
			newline = line.replace(old_function,invoked_function)
			newline = re.sub(r'\s*',"",newline)
			if line.find("(")!=-1: #si no tiene parentesis en global var
				variables = line.split("(")[1]
			else:
				variables=""
			newline = "json.loads("+invoked_function + "("+ variables + ")"
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
			else:
				if "(" in variables:
					#bla bla bla
					#variables_aux = variables.split("(")
					ind_aux = variables.find("(") # indice, porque puede haber varios parentesis (si usas una tupla por ejemplo)
					variable_aux = variables[ind_aux:len(variables)]#"("+variables.split("(")[-1]
					variables = variables.replace(variable_aux,"")
					newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+'"'+invoked_function+"."+variables+"('+str"+variable_aux+"+')\"'"+"+' , '+"+"str(ver_"+old_function+"))"
				else:
					#newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"."+old_function+"','"+invoked_function+"."+variables+"')[0]"
					newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+invoked_function+"."+variables+"')[0]"
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
			#podria omitir el campo 0 aqui
			#Pongo el campo 0, porque en las operaciones de cambio, solo queremos el nuevo valor, la version no se pide nunca en el codigo
		#Si es funcion normal:
		#newline = "invoker(['du_"+str(invoked_du)+"'], '"+invoked_function+"','"+invoked_function+"."+variables+"')[0]"
		
	print("POST:funcion, du invocada:",invoked_function,invoked_du)
	return newline

def writeGlobalCode_old(fun_name,fo, globalName,module ,con, config_dict, tabs):
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
		for i in tabs:
			tabulations+="\t"
	fun_name = fun_name.split(" ")[1]
	cursor = con.cursor()
	print "SELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+module+"._VAR_"+globalName+"'"
	cursor.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+module+"._VAR_"+globalName+"'")
	row = cursor.fetchone()
	global_fun_du = row[0]
	global_fun_name = row[1]
	#pillo el final name para que los atributos se llamen de forma correcta
	cursor.execute("SELECT FINAL_NAME from functions where ORIG_NAME = '"+module+"."+fun_name+"'")
	row = cursor.fetchone()
	final_fun_name = row[0]
	if (module+"."+fun_name) in config_dict["labels"]:#Aniado parallel si es el codigo de la funcion parallel
		if config_dict["labels"][module+"."+fun_name] == 'PARALLEL':
			final_fun_name = "parallel_"+final_fun_name
	#print "\t\t Empezamos a escribir el codigo de la variable global"
	fo.write("#Automated code for global var:\n #fun_name: "+ fun_name+" final fun name: "+final_fun_name+" globalName: "+ globalName+ " destiny du: "+ str(global_fun_du)+" global_fun_name: "+ global_fun_name+"\n")
	#fo.write("#Automated code for global var:\n #fun_name: "+ fun_name+" globalName: "+ globalName+ " destiny du: "+ str(global_fun_du)+" global_fun_name: "+ global_fun_name+"\n")

	fo.write('''#============================global vars automatic code=========================
	#'''+globalName+'''
	if not hasattr('''+final_fun_name+''', "'''+globalName+'''"):
		'''+final_fun_name+'''.'''+globalName+''' = None

	if not hasattr('''+final_fun_name+''', "ver_'''+globalName+'''"):
		'''+final_fun_name+'''.ver_'''+globalName+''' = 0
        
	aux_'''+globalName+''',aux_ver = invoker(['''+"'du_"+str(global_fun_du)+"'"+'''],'''+"'"+global_fun_name+"'"+''',"'None',"+str('''+final_fun_name+'''.ver_'''+globalName+'''))
	if aux_'''+globalName+''' != "None":
		'''+final_fun_name+'''.'''+globalName+''' = aux_'''+globalName+'''
	'''+globalName+"="+final_fun_name+"."+globalName+'''
	'''+final_fun_name+'''.ver_'''+globalName+"= aux_ver"'''
	'''+"ver_"+globalName+"= "+final_fun_name+'''.ver_'''+globalName+'''
		''')

	return "hola"

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
	print "SELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+module+"._VAR_"+globalName+"'"
	cursor.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+module+"._VAR_"+globalName+"'")
	row = cursor.fetchone()
	global_fun_du = row[0]
	global_fun_name = row[1]
	#pillo el final name para que los atributos se llamen de forma correcta
	cursor.execute("SELECT FINAL_NAME from functions where ORIG_NAME = '"+module+"."+fun_name+"'")
	row = cursor.fetchone()
	final_fun_name = row[0]
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
        
	'''+tabulations+'''aux_'''+globalName+''',aux_ver = invoker(['''+"'du_"+str(global_fun_du)+"'"+'''],'''+"'"+global_fun_name+"'"+''',"'None',"+str('''+final_fun_name+'''.ver_'''+globalName+'''))
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
			return json.dumps(('''+final_name+'''.'''+fun_name+''','''+final_name+'''.ver_'''+fun_name+'''))
	else:
		try:
			'''+final_name+'''.ver_'''+fun_name+'''+=1
			return json.dumps((eval(op),'''+final_name+'''.ver_'''+fun_name+'''))
		except:
			with lock_'''+final_name+"."+fun_name+''':
				exec(op)
				'''+final_name+'''.ver_'''+fun_name+'''+=1
			return json.dumps(("done",'''+final_name+'''.ver_'''+fun_name+'''))''')