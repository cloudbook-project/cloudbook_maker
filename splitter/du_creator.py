#create the deployable units

def create_dus(con,matrix,input_path,output_path):
	#primero entramos en la tabla de fucniones, y para las funcinoes colapsadas, les actualizamos el ud
	ud_itf_dict={}
	for i in range(1,len(matrix[0])-1):
		create_du(con,i,input_path,output_path,ud_itf_dict)
	'''por ultimo creamos las UD_itf'''
	#create_uds_itf(ud_itf_dict)


def create_du(con,i,input_path,output_path):
	#i is a list of functions
	#para cada elemento j, de i: 
		#extraer su nombre de modulo original
		#entrar en la tabla modules y coger los imports traducidos, y guardarlos en un lista de imports finales
	#look in functions table for the first funtion name that matches with i[0]
	#this row UD will be the name of this deployable unit and it will contains all function from list i
	#create ud file and open it for write
	#escribir en el fichero la lista de imports finales
	#for each function name in i:
		#enter in file, copy the function text,
		#process the function name translating invocations with final invocations
		#and include it into the ud file
	pass

def translate_invocation(con,orig_module,orig_function_name,invoked_function,i,ud_itf_dict):
	'''orig function invokes invoked function
	si la funcion invocada no esta en i, la traduccion incluira el itf, 
		Ej: du45_itf.f
	guardamos en un diccionario las itfs creadas para poder generar luego Uds_itf
	no repetmos funciones que ya esten en alguna entrada del diccionario
	ej: {ud-xx_itf:[f1,f2],...}
	'''
	pass

