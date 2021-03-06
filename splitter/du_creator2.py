from __future__ import print_function
import ast #for translating unicode strings
import re
import os
import du_utils as utils
import time as ttime

import sys
import json


function_mapping={}

def save_function_mapping(config_dict):
	print ("------ function mapping ------")
	print (function_mapping)
	
	output_dir= config_dict["distributed_fs"]+os.sep+"distributed"+os.sep+"matrix"
	
	#write output file in json format
	#---------------------------------
	json_str = json.dumps(function_mapping)
	fo = open("dd", 'w')
	fo = open(output_dir+"/function_mapping.json", 'w')
	fo.write(json_str)
	fo.close()

def create_dus(config_dict):
	con=config_dict["con"]
	matrix=config_dict["matrix_filled"]
	input_path=config_dict["input_dir"]
	output_path=config_dict["output_dir"]

	print("dus: ",range(1,len(matrix[0])))
	du_list =[]
	for i in range(1,len(matrix[0])):
		du_list.append(create_du(con,matrix[0][i],input_path,output_path, config_dict,du_list))
	
	save_function_mapping(config_dict)
	return du_list


def create_du(con,function_list,input_path,output_path, config_dict, du_list):
	print( "\t============== create du ===============")
	print( "\tFunction list:", function_list)
	#vars
	pragmas = ["#__CLOUDBOOK:PARALLEL__","#SYNC","#__CLOUDBOOK:RECURSIVE__","#__CLOUDBOOK:LOCAL__",r'#SYNC:\d']
	invocation_pragmas = ["#__CLOUDBOOK:NONBLOCKING__"]
	cursor = con.cursor()
	#if the function list is only one function as a string, convert into list
	if isinstance(function_list, list) == False:
		function_list = function_list.split()
	
	#ud guide: 1: Name assgination of du, the du number of the first du in the list
	du_name = utils.du_name_assignation(con, function_list, du_list,config_dict) #du_list is passed in order to not repeat du names
	#ud guide 2: Unifying imports and create final imports list
	final_imports = utils.get_final_imports(con, function_list)
	
	#ud guide 3: ud creation
	#ud guide 3.1: create du file, write imports and invoker
	output_file = output_path+os.sep+du_name+".py"
	fo = open(output_file, 'w')
	for i in final_imports:
		fo.write(i)
		fo.write("\n")
	fo.write("\n")
	#write consts
	for i in config_dict["constants"]:
		fo.write(i)
		fo.write("\n")
	for i in config_dict["nonshared"]:
		fo.write(i)
		fo.write("\n")
	fo.write("invoker=None\n")
	fo.write("cloudbook_sync_timeout=False\n\n")  #Se puede quitar de aqui y generarla solo cuando es necesaria
	#write classes
	for i in config_dict["class"]:
		fo.write(config_dict["class"][i])
		fo.write("\n")

	#List of nonblocking invocations, in order to make the code on the fly
	nonblocking_functions=[]
	
	#ud guide 3.2: Main loop, for every function in the du get name info, and write in fo if belongs to the actual du
	for i in function_list:
		#ud guide 3.2.1: Get names of function (module, complete name, etc...) 
		print( "\tFor function "+i)
		#get module and function name. module in left to last dot, name of function, right of last dot
		module = i[:i.rfind('.')]
		name = i[i.rfind('.')+1:len(i)]
		final_name = utils.get_final_name(con, i)
		print("\t\tModule: ", module, " Name:", name, " Final Name: ", final_name)
		function_mapping[module+"."+name]=final_name
		#assign optional arguments, markers for class and fun
		isfun=False
		translated_fun = False #This marker is used in order to make external invocations without copy the local invocation too.
		isClass = False
		##These variables are used to save the actual and the previows line in order to apply the invocation pragmas.
		actual_line = ""
		last_line = ""
		#ud guide 3.2.2: Get input path, and open it for reading
		input_file = input_path+os.sep+module.replace('.',os.sep)+".py"
		print( "\tOpen the file: "+ input_file)
		fi = open(input_file,'rU')
		for i,line in enumerate(fi,1):
			#ud guide: 3.2.2.1
			tabs = line.count('\t')
			#ignore comments
			clean_line = re.sub(r'\s*',"",line)
			actual_line = clean_line
			if ("#" in clean_line) and (clean_line not in pragmas) and (clean_line not in invocation_pragmas) and ("#SYNC:" not in clean_line):
				continue
			#Adaptamos o incorporamos a nombre funcion, a def loquesea o declaracion de variable global
			if "_VAR_" in name:
				fun_name = name.replace("_VAR_","")
			else:
				fun_name = "def " + name
			###Translate prints
			#ud guide: 3.2.2.3 Lo quito por ahora
			###Three kinds of fun in file
			#ud guide: 3.2.2.4
			lock_parallel = False
			if (fun_name in line) and (tabs==0):
				print( "\t\tHemos encontrado la funcion: ", name, " que sera ", final_name)
				if "_VAR_" in name:
					#fo.write(line.replace(fun_name,final_name+" con el valor"))#CODIGO DE FUNCION DE VARIABLE GLOBAL
					#Valor de la variable global
					if "=" not in line:#Is not an assignation
						continue
					gl_value = line.split("=")[1]
					#t.value = re.sub(r'\s*',"",t.value)
					gl_value = re.sub(r'\s*',"",gl_value)
					line3 = utils.writeGlobalDef(fun_name, final_name, gl_value, fo, con)
					continue
				else:
					#Si es Parallel escribo nombre y codigo de hilos, y nuevo nombre,
					#a continuacion sigo escribiendo igual
					if module+"."+name in config_dict["labels"]:
						if config_dict["labels"][module+"."+name] == 'PARALLEL':
							funvariables = line[line.find("("):len(line)-2]#el -2 para quitar el ":" final y el \n
							print( funvariables)
							fo.write(line.replace(name, final_name))#original fun name
							#write thread code 
							'''print("Esto es una prueba NONBLOCKING soy el fichero B")
							hilo1 = threading.Thread(target=blockingB, daemon = False)
							hilo1.start()
							return "Ya he llamado"'''
							funvariables=funvariables.replace("(","[")
							funvariables=funvariables.replace(")","]")
							if "=" in funvariables:
								fo.write('''	thread'''+final_name+''' = threading.Thread(target= parallel_'''+final_name+''', daemon = False, kwargs = dict('''+funvariables[1:len(funvariables)-1]+'''))
	thread'''+final_name+'''.start()
	return json.dumps("thread launched")

''')
							else:
								fo.write('''	thread'''+final_name+''' = threading.Thread(target= parallel_'''+final_name+''', daemon = False, args = '''+funvariables+''')
	thread'''+final_name+'''.start()
	return json.dumps("thread launched")

''')
							#fo.write('''	thread'''+final_name+''' = threading.Thread(target= parallel_'''+final_name+''', daemon = False, args = '''+funvariables+''')
#	thread'''+final_name+'''.start()
#	return json.dumps("thread launched")
#
#''')
							final_name = "parallel_"+final_name	
							'''if not hasattr(f1, "lock_body_list"):
		f1.lock_body_list = threading.Lock()
							'''
							lock_parallel_line = '''	if not hasattr('''+final_name+''', "lock"):
		'''+final_name+'''.lock = threading.Lock()
	with '''+final_name+'''.lock:
'''
						if config_dict["labels"][module+"."+name] == 'RECURSIVE':	
							final_name = "recursive_"+final_name					

					fo.write(line.replace(name, final_name))
					if "parallel_" in final_name:
						fo.write(lock_parallel_line)
				isfun = True
			#ud guide: 3.2.2.5
			lock_parallel = False
			if (fun_name not in line) and (isfun):
				print( "\n\t\tMiramos dentro de la funcion"+fun_name+" "+module+"."+name)
				if module+"."+name in config_dict["labels"]:
					if config_dict["labels"][module+"."+name] == 'PARALLEL':
						print("Activo el lock parallel")
						lock_parallel = True
				if "print" in line:
					print("OJOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO PRINTTTTT",line)
					#fo.write(line)
					if lock_parallel == True:
						line = '\t'+line
						fo.write(line)
						
					else:
						fo.write(line)
					continue
				if "global" in line:#todo, no traducir si es nonshared
					#comprobar si es nonshared
					namevar = line.split("global")[1]
					namevar = re.sub(r'\s*',"",namevar)
					dont_translate = False
					print("namevar",namevar)
					for nonsharedvar in config_dict["nonshared"]:
						nonshared = nonsharedvar.split("=")[0]
						nonshared = re.sub(r'\s*',"",nonshared)
						print("nonshared",nonshared)
						print(str(nonshared == namevar))
						if nonshared == namevar:
							print("iguales")
							if lock_parallel == True:
								fo.write("\t"+line)
							else:
								fo.write(line)
							print("eeeeeeeeeeeeeeeeeeeehhhhhhhhhhhhhhhhhhhhh")
							dont_translate = True
					if dont_translate == True:
						dont_translate = False
						continue
					#si es nonshared hago continue
					line2 = "#"+ line + "#Aqui va el chorrazo de codigo"
					globalName = line.split(" ")[1]
					#globalName = globalName.replace("\n","")
					globalName = re.sub(r'\s*',"",globalName)
					if lock_parallel == True:
						line3 = utils.writeGlobalCode(fun_name, fo, globalName,module, con, config_dict, tabs+1)
						
					else:
						line3 = utils.writeGlobalCode(fun_name, fo, globalName,module, con, config_dict, tabs)
					#print line3
					if lock_parallel == True:
						line2 = "\t"+line2
						fo.write(line2.replace("\n","")+"\n")
						
					else:
						fo.write(line2.replace("\n","")+"\n")
					continue
				if "#SYNC" in line:
					if line.find(":") != -1:
						time = line.split(":")[1]
						time = time.replace(":","")
						time = int(time)*100#/10
						time = str(time)
					#line = line.replace("#SYNC",'''while json.loads(cloudbook_th_counter("")) > 0: #This was sync
			#sleep(0.01)
			#''')
					#todo: Los tabs bien
						line = "\t"*tabs+'''temp = 0
		timeout = True
		while json.loads(cloudbook_th_counter("")) > 0 and timeout: #This was sync
			if temp > '''+time+''':
				print("threading failure")
				globals()['cloudbook_sync_timeout']=True
				timeout = False
			time.sleep(0.01)
			temp+=1
'''
					else:
						line = "\t"*tabs+'''while json.loads(cloudbook_th_counter("")) > 0: #This was sync
			time.sleep(0.01)
'''
					fo.write(line)
					continue
				#Hay que ver si dentro de la funcion, se llama a alguna otra funcion de la tabla functions
				#hago una query de los orignames y los guardo en una lista
				if translated_fun == True:
					translated_fun = False
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
				print( "\t\t\tBuscamos estas: ", orig_list)
				#miro si la fun (segunda parte de la tupla) esta en line
				#globaldict = False
				global_asig = False
				for j in orig_list:
					if j[1] in line:#nombre solo fun
						print( "\t\t\tEncuentro esta: ", j[1], " aqui", i, ": ", line)
						#reconocer la invocacion en la linea
						aux_line = line
						invocation_index = 0#to do, usarlo para escribir bien la linea, solo traducir la invocacion
						aux_line = aux_line.split()
						print( "\t\t\tEsta escrita asi", aux_line)
						for i,elem in enumerate(aux_line):
							if j[1] in elem:
								aux_line = aux_line[i]
								invocation_index = i								

						invocation_fun = aux_line
						print( "\t\t\tINVOCATION FUN=="+invocation_fun)
						if "_VAR_" in j[0]:#Es una variable global solo tocamos modificaciones, con parentesis
							if invocation_fun.find("(")!=-1:
								invocation_fun = "_VAR_"+invocation_fun[:invocation_fun.rfind("(")]
								if invocation_fun.find(".")!=-1:
									invocation_fun = invocation_fun.split(".")[0]
							elif ("=" in line) and (invocation_index==0): #TODO es una asignacion y hay que traducirla
							#Tiene que estar antes del igual
								global_asig = True
								invocation_fun = "_VAR_"+invocation_fun
								print("asignacion global",line)
								if (invocation_fun.find("[")!=-1):
									invocation_fun = invocation_fun[:invocation_fun.rfind("[")]
									#globaldict = True
							else:
								print("Esta linea no la entiendo:", line)
								continue						
							#else:# No tiene parentesis
							#	invocation_fun = "_VAR_"+invocation_fun
							#if invocation_fun.find(".")!=-1:
								#invocation_fun = invocation_fun.split(".")[0]
							#if invocation_fun.find(":")!=-1:#Hacer esto para todos los elementos raros
							#	invocation_fun = invocation_fun.replace(":","")
						else:
							invocation_fun = invocation_fun[:invocation_fun.rfind("(")]
						print( "\t\t\tLa invocacion que buscamos es", invocation_fun, " y en FUNCTIONS es ", j[0])
						if j[0] == invocation_fun:
							print( "\t\t\tEsta bien escrita")
							complete_name = invocation_fun
						else:
							#Esto es solo si el modulo tiene un punto, si no, peta
							if module.rfind('.')!=-1:							
								complete_name = module[:module.rfind('.')+1]+invocation_fun
							else:
								complete_name = module+'.'+invocation_fun
							print( "\t\t\tCompletamos nombre y queda: ", complete_name)
							if complete_name != j[0]:#OJO ESTO ES PARA EVITAR CONFUSIONES CON INVOCACIONES EN EL LADO DERECHO
								print("No me interesa")
								continue
						print( "\t\t\tVAMOS A TRADUCIR")
						nonblocking_invocation = False
						if last_line in invocation_pragmas:
							if last_line == "#__CLOUDBOOK:NONBLOCKING__":
								nonblocking_invocation = True
								print("====================================NONBLOCKING:", complete_name)
								nonblocking_functions.append((complete_name, line))
						new_line = utils.translate_invocation(con,module,fun_name,complete_name,function_list,fo,du_name,line,tabs,name,nonblocking_invocation,config_dict)
						nonblocking_invocation = False
						#new_line = utils.translate_invocation(con,module,fun_name,complete_name,function_list,fo,du_name,line,tabs,name,config_dict)
						print("===Acabamos de traducir la linea",line,"por",new_line)
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

						if lock_parallel == True:
							tabs +=1							
						for t in range(tabs):
							new_line = "\t"+new_line
						fo.write(new_line)
						fo.write("\n")
						if global_asig: #copy also the local assignation
							clean_line = re.sub(r'\s*',"",line)
							for t in range(tabs):
								clean_line = "\t"+clean_line
							fo.write(clean_line)#ver si las tabs van bien, mejor limpio la linea y le meto tabs
							fo.write("\n")
							global_asig = False						
						print("\t\t\tPongo a true TRANSLATED FUN")
						translated_fun = True
				if "return" in line:
					print( "\t\t\tAQUI RETURN")
					if module+"."+name in config_dict["labels"]:
						if config_dict["labels"][module+"."+name] == 'LOCAL':
							pass
					else:	
						aux_ret = line.split()[-1]
						if lock_parallel == True:
							line = line.replace(aux_ret,"json.dumps("+aux_ret+")")
							line = "\t"+line
							
						else:
							line = line.replace(aux_ret,"json.dumps("+aux_ret+")")
				if translated_fun==False:
						print("\t\t\tES UNA LINEA NORMAL")
						if lock_parallel == True:
							line = "\t"+line
							fo.write(line)							
						else:
							fo.write(line)
				lock_parallel = False
			#ud guide: 3.2.2.6
			if (fun_name not in line) and (tabs==0):
				#Hara falta traducir aqui
				isfun = False
			last_line = actual_line
		#ud guide: 3.2.3
		if "parallel_" in final_name:#Before return, sychronize thread
			#pre_line = '''invoker(['du_0'], 'cloudbook_th_counter',"'--'")
			#''' 
			fo.write("\n\t\tinvoker(['du_0'], 'cloudbook_th_counter',\"'--'\")\n")
			fo.write("\n\t\treturn json.dumps('cloudbook: done') \n\n")
		#ud guide: 3.2.4
		if "parallel_" not in final_name:
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
	return json.dumps(cloudbook_th_counter.val)

''')
		fo.write('''def main():
	#f0()
	#return "cloudbook: done"
	return f0()

''')

		fo.write('''if __name__ == '__main__':
	f0()
			''')
	if len(nonblocking_functions)!=0:
		fo.write("\n")
		funvariables="[]"
		#fo.write(str(len(nonblocking_functions)) + str(nonblocking_functions))
		marked_nonblocking_functions = []
		for i in nonblocking_functions:
			if i[0] in marked_nonblocking_functions: #not copy repeated functions
				continue
			marked_nonblocking_functions.append(i[0])
			utils.write_nonblocking_invocation(i,fo,con)
	fo.close()
	return du_name