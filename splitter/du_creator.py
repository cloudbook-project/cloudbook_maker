#create the deployable units
import ast #for translating unicode strings

def create_dus(con,matrix,input_path,output_path):
	print "dus: ",range(1,len(matrix[0]))
	for i in range(1,len(matrix[0])):
		create_du(con,matrix[0][i],input_path,output_path)


def create_du(con,function_list,input_path,output_path):
	print "============== create du ==============="
	#look in functions table for the first funtion name that matches with function_list[0]
	#this row UD will be the name of this deployable unit and it will contains all function from function_list
	print "Function list:", function_list
	cursor = con.cursor()
	cursor.execute("SELECT DU from FUNCTIONS where ORIG_NAME=="+"'"+function_list[0]+"'")
	du_name = "du_"+str(cursor.fetchone()[0])
	print "Va a ser la du: ", du_name

	#para cada elemento j, de function_list: 
		#extraer su nombre de modulo original
		#entrar en la tabla modules y coger los imports traducidos, y guardarlos en un lista de imports finales sin repeticion
		#eliminar de la lista si existiese, el import de la ud que estamos creando
	final_imports = []
	for i in function_list:
		module_name = i[:i.rfind('.')] #extraer su nombre de modulo original
		print "module_name de",i,"es",module_name 
		cursor.execute("SELECT FINAL_IMPORTS from MODULES where ORIG_NAME=="+"'"+module_name+"'")
		#translate unicode to list of strings
		for n in cursor.fetchone():
			print "\t Imports en la bbdd:",n
			try:
				sub_list = ast.literal_eval(n)
				final_imports.extend(sub_list)
			except ValueError:
				final_imports.append(str(n))
	final_imports = list(set(final_imports)) #remove duplicates
	#remove auto_import
	for i,elem in enumerate(final_imports):
		if du_name in elem:
			print "autoimport en la poscion ",i, ":", elem
			final_imports.remove(elem)

	print "Final Imports: ", final_imports		


	#create ud file and open it for write
	#escribir en el fichero la lista de imports finales, excepto 
	#for each function name in function_list:
		#enter in original file, copy the function text,
		#analizar el texto y buscar la primera funcion de la tabla de funciones, en caso de encontrarla
		#se traduce, despues se hace lo mismo con la segunda fun de la tabla de funciones, y asi hasta el final
		#El proceso de traduccion consiste en(se puede hacer en translate invocation):
			#ver translate_invocation()
		#after translation of invocations of function text, include it into the du file
	output_file = output_path+"/"+du_name+".py"
	fo = open(output_file, 'w')
	for i in final_imports:
		fo.write(i)
		fo.write("\n")
	fo.write("\n")
	for i in function_list:
		aux_ind = i.rfind('.')
		module = i[:i.rfind('.')]
		name = i[i.rfind('.'):len(i)]
		name = name[1:len(name)]
		print "\t",module, name
		print input_path
		input_file = input_path+"/"+module.replace('.','/')+".py"
		fi = open(input_file,'r')
		isfun=False
		for i,line in enumerate(fi,1):
			tabs = 0
			tabs += line.count('\t')
			linea = line.split()
			fun_name = "def " + name
			if (fun_name in line) and (tabs==0):
				fo.write(line)
				isfun = True
			if (fun_name not in line) and (isfun):
				#fo.write(line)
				#print line#################################Translate aqui
				if "()" in line:
					#print "aqui hay funcion", line
					invoked_fun = ""
					invoked_fun=line[:line.rfind("(")]
					invoked_fun=invoked_fun.replace("\t","")
					#print "invokedfun",invoked_fun
					#llamar a traduccion
					print "hay que traducir:"+line+ " en modulo, fun name, invokedfun: "+module,fun_name,invoked_fun
					translate_invocation(con,module,fun_name,invoked_fun,function_list,fo,du_name,line,tabs)#falta numero tabulaciones
				else:
					fo.write(line)

			if (fun_name not in line) and (tabs==0):
				#Hara falta traducir aqui
				isfun = False
	fi.close()
	if (du_name == "du_0"):
		fo.write('''if __name__ == '__main__':
	main()
			''')
	fo.close()


def translate_invocation(con,orig_module,orig_function_name,invoked_function,function_list,file_descriptor,du_name,line,tabs):
	#El proceso de traduccion consiste en:
			#si la funcion esta en la misma du(estara en la function list) se invoca sin nombre de modulo
			#else invoke("du_xx.f(...)"), la du_xx la sacamos de la tabla de funciones
	c = con.cursor()
	newline = ""
	#invoked_function = "dir1.file1.f1"
	c.execute("SELECT DU from functions where ORIG_NAME like '%"+invoked_function+"%'")
	invoked_du = c.fetchone()[0]
	if str(invoked_du) in du_name:
		invoked_function = invoked_function[invoked_function.rfind(".")+1:len(invoked_function)]
		newline = invoked_function+"()"+"#Translated from precedent line"
	else:
		invoked_function = invoked_function[invoked_function.rfind("."):len(invoked_function)]
		newline = "invoke(du_"+str(invoked_du)+invoked_function+"())"+"#Translated from precedent line"
	for i in range(tabs):
		newline = "\t"+newline
	file_descriptor.write(newline)
	file_descriptor.write("\n")

