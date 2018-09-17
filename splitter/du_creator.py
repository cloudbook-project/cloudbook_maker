#create the deployable units
import ast #for translating unicode strings

def create_dus(con,matrix,input_path,output_path):
	print "dus: ",range(1,len(matrix[0]))
	for i in range(1,len(matrix[0])):
		create_du(con,matrix[0][i],input_path,output_path)


def create_du(con,function_list,input_path,output_path):
	print "\t============== create du ==============="
	#look in functions table for the first funtion name that matches with function_list[0]
	#this row UD will be the name of this deployable unit and it will contains all function from function_list
	print "\tFunction list:", function_list
	cursor = con.cursor()
	cursor.execute("SELECT DU from FUNCTIONS where ORIG_NAME=="+"'"+function_list[0]+"'")
	du_name = "du_"+str(cursor.fetchone()[0])
	print "\tVa a ser la du: ", du_name

	#para cada elemento j, de function_list: 
		#extraer su nombre de modulo original
		#entrar en la tabla modules y coger los imports traducidos, y guardarlos en un lista de imports finales sin repeticion
		#eliminar de la lista si existiese, el import de la ud que estamos creando
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
	cursor = con.cursor()
	output_file = output_path+"/"+du_name+".py"
	fo = open(output_file, 'w')
	for i in final_imports:
		fo.write(i)
		fo.write("\n")
	fo.write("\n")
	fo.write("invoker=None\n\n")

	for i in function_list:
		aux_ind = i.rfind('.')
		module = i[:i.rfind('.')]
		name = i[i.rfind('.'):len(i)]
		name = name[1:len(name)]
		cursor.execute("SELECT FINAL_NAME from FUNCTIONS where ORIG_NAME = '"+i+"'")
		final_name = cursor.fetchone()[0]
		#print "\tmodule, name: ",module, name
		#print "\tinput path: ",input_path
		input_file = input_path+"/"+module.replace('.','/')+".py"
		fi = open(input_file,'r')
		isfun=False
		for i,line in enumerate(fi,1):
			translated_fun = False
			tabs = 0
			tabs += line.count('\t')
			linea = line.split()
			fun_name = "def " + name
			###Translate prints
			newprint = ""
			newvar = ""
			if "print " + '"@' in line:
				print "AQUI PRINT"
				line_aux = line.split("@",1)
				print line_aux[1]
				arg_aux = '"'+line_aux[1].rstrip()
				arg_aux = "eval("+arg_aux+")"
				print "Argumento Llamada", arg_aux
				
				for i in range(tabs):
					newprint = "\t"+newprint
					newvar = "\t"+newvar
				if du_name == "du_0":
					newvar = newvar + "cloudbook_txt = " + arg_aux + "\n"
					newprint = newprint + 'cloudbook_print(cloudbook_txt)'
					line = newvar+ "\n" + newprint+"\n"
				else:
					#arg_aux = "'"+arg_aux+"'"
					newvar = newvar + "cloudbook_txt = " + arg_aux + "\n" 
					newprint = newprint + 'invoker("du_0.cloudbook_print('+'"+cloudbook_txt+"'+')")'
					line = newvar+ "\n" + newprint+"\n"
			###Three kinds of fun in file
			if (fun_name in line) and (tabs==0):
				print "\t\tHemos encontrado la funcion: ", name, " que sera ", final_name
				fo.write(line.replace(name, final_name))
				isfun = True
			if (fun_name not in line) and (isfun):
				print "\t\tMiramos dentro de la funcion"
				#Hay que ver si dentro de la funcion, se llama a alguna otra funcion de la tabla functions
				#hago una query de los orignames y los guardo en una lista
				cursor.execute("SELECT ORIG_NAME from FUNCTIONS")
				row = cursor.fetchall()
				orig_list = [] #list of orignames
				for j in row:
					orig_fun_name = j[0]
					trunc = orig_fun_name.rfind(".")+1
					orig_fun_name = orig_fun_name[trunc:len(orig_fun_name)]
					orig_list.append((j[0].encode('ascii'),orig_fun_name.encode('ascii')))#tuplas(nombreorig,solofun)
				print "\t\t\tBuscamos estas: ", orig_list
				#miro si la fun (segunda parte de la tupla) esta en line
				for j in orig_list:
					if j[1] in line:#nombre solo fun
						print "\t\t\tEncuentro esta: ", j[1], " aqui", i, ": ", line
						#supongo q la linea es solo la invocacion
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
						invocation_fun = invocation_fun[:invocation_fun.rfind("(")]
						print "\t\t\tLa invocacion que buscamos es", invocation_fun, " y en FUNCTIONS es ", j[0]
						if j[0] == invocation_fun:
							print "\t\t\tEsta bien escrita"
							complete_name = invocation_fun
						else:
							complete_name = module[:module.rfind('.')+1]+invocation_fun
							print "\t\t\tCompletamos nombre y queda: ", complete_name
						new_line = translate_invocation(con,module,fun_name,complete_name,function_list,fo,du_name,line,tabs)
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
				if translated_fun==False:
						fo.write(line)
			if (fun_name not in line) and (tabs==0):
				#Hara falta traducir aqui
				isfun = False
		
		
				
		fo.write("\n\treturn 'cloudbook: done' \n\n")					

	fi.close()
	if (du_name == "du_0"):
		fo.write('''def cloudbook_print(element):
	print element
	return "cloudbook: done"
	
''')
		fo.write('''def main():
	f0()
	return "cloudbook: done"

''')

		fo.write('''if __name__ == '__main__':
	f0()
			''')
	fo.close()


def translate_invocation(con,orig_module,orig_function_name,invoked_function,function_list,file_descriptor,du_name,line,tabs):
	#El proceso de traduccion consiste en:
			#si la funcion esta en la misma du(estara en la function list) se invoca sin nombre de modulo
			#else invoke("du_xx.f(...)"), la du_xx la sacamos de la tabla de funciones
	c = con.cursor()
	newline = ""

	#c.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME like '%"+invoked_function+"%'")
	c.execute("SELECT DU,FINAL_NAME from functions where ORIG_NAME = '"+invoked_function+"'")
	row = c.fetchone()
	invoked_du = row[0]
	invoked_function = row[1]
	if str(invoked_du) in du_name:
		#invoked_function = invoked_function[invoked_function.rfind(".")+1:len(invoked_function)]
		newline = invoked_function+"()"
	else:
		#invoked_function = invoked_function[invoked_function.rfind("."):len(invoked_function)]
		#newline = "invoke('du_"+str(invoked_du)+"' , '"+invoked_function+"()')"
		newline = "invoker('du_"+str(invoked_du)+"."+invoked_function+"()')"
	#for i in range(tabs):
		#newline = "\t"+newline
	#file_descriptor.write(newline)
	#file_descriptor.write("\n")
	return newline
