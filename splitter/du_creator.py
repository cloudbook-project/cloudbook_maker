#create the deployable units

def create_dus(con,matrix,input_path,output_path):
	for i in range(1,len(matrix[0])-1):
		create_du(con,i,input_path,output_path)


def create_du(con,function_list,input_path,output_path):
	#look in functions table for the first funtion name that matches with i[0]
	#this row UD will be the name of this deployable unit and it will contains all function from function_list

	#para cada elemento j, de function_list: 
		#extraer su nombre de modulo original
		#entrar en la tabla modules y coger los imports traducidos, y guardarlos en un lista de imports finales sin repeticion
		#eliminar de la lista si existiese, el import de la ud que estamos creando
	
	#create ud file and open it for write
	#escribir en el fichero la lista de imports finales, excepto 
	#for each function name in function_list:
		#enter in original file, copy the function text,
		#analizar el texto y buscar la primera funcion de la tabla de funciones, en caso de encontrarla
		#se traduce, despues se hace lo mismo con la segunda fun de la tabla de funciones, y asi hasta el final
		#El proceso de traduccion consiste en(se puede hacer en translate invocation):
			#ver translate_invocation()
		#after translation of invocations of function text, include it into the du file
	pass

def translate_invocation(con,orig_module,orig_function_name,invoked_function,function_list):
	#El proceso de traduccion consiste en:
			#si la funcion esta en la misma du(estara en la function list) se invoca sin nombre de modulo
			#else invoke("du_xx.f(...)"), la du_xx la sacamos de la tabla de funciones
	pass

