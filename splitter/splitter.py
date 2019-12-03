import iterator
import du_creator2 as du_creator
import time

def split_program(config_dict):
	#con=config_dict["con"]
	matrix=config_dict["matrix_data"]
	#input_path=config_dict["input_dir"]
	#output_path=config_dict["output_dir"]
	#desired_num_deployable_units=config_dict["num_dus"]

	print (">>>ENTER in split_program()...")
	print_matrix(matrix)
	#matrix = iterator.iterate(con,matrix,desired_num_deployable_units)
	matrix = iterator.iterate(config_dict)
	config_dict["matrix_filled"]=matrix

	print ("\nTHE COLLAPSED FINAL MATRIX IS:")
	print_matrix(matrix)
	#AnADIMOS PARALLELS
	print(config_dict["labels"])
	#add_labeled_functions(config_dict)
	separate_default_functions(config_dict)
	print ("\nTHE COLLAPSED FINAL MATRIX WITH PARALLEL IS:")
	print_matrix(config_dict["matrix_filled"])
	if config_dict["non-reliable_agent_mode"] == True:
		make_du0_dependable(config_dict)
		print ("\nTHE COLLAPSED FINAL MATRIX WITH du_0 du0_dependable IS:")
		print_matrix(config_dict["matrix_filled"])
	if len(config_dict["du0_functions"]) != 0:
		add_du0_functions(config_dict)
		print ("\nTHE COLLAPSED FINAL MATRIX WITH du_0 functions:")
		print_matrix(config_dict["matrix_filled"])
	update_du0_functions(config_dict)
	du_list=[]
	du_list = du_creator.create_dus(config_dict)


	print (">>>EXIT from split_program...")
	return du_list

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])

def add_labeled_functions(config_dict):
	matrix = config_dict["matrix_filled"]
	num_cols=len(matrix[0])
	#num_rows=len(matrix[0])
	for i in range(1,num_cols):
		for j in config_dict["labels"]:
			if (config_dict["labels"][j] == 'PARALLEL') or (config_dict["labels"][j] == 'RECURSIVE') or (config_dict["labels"][j] == 'LOCAL'):# or (config_dict["labels"][j] == 'CLASS_DEF'):
				print("PARALLEL", j)
				if type(matrix[0][i])==list:
					if j not in matrix[0][i]:
						matrix[0][i].append(j)
						#matrix[i][0].append(j)
				else:
					if j != matrix[0][i]:
						matrix[0][i] = [matrix[0][i],j]

def separate_default_functions(config_dict):
	'''this function separate all parallel and recursive functions in other du_list'''
	print(">>> ENTER IN separate_default_functions")
	print("labels",config_dict['labels'])
	matrix = config_dict["matrix_filled"]
	con = config_dict["con"]
	default_list = []
	final_list = []
	local_list = []
	dus = matrix[0]
	dus.remove('Matrix')
	du_index = 0
	for function_list in dus:
		print("para las funciones", function_list)
		if isinstance(function_list, list) == False:
			aux_function_list = function_list.split()
		else:
			aux_function_list = function_list
		for i in aux_function_list:
			if i in config_dict["labels"]:
				if ((config_dict["labels"][i] == 'LOCAL') or (config_dict["labels"][i] == 'RECURSIVE') or (config_dict["labels"][i] == 'PARALLEL')):
					print("las meto")
					default_list.append(i)
				if (config_dict["labels"][i] == 'LOCAL'):
					local_list.append(i)
					#final_list.append(i)
				else:
					final_list.append(i)
					#print("meto esta",i)
			else:
				final_list.append(i)
				#print("meto esta",i)
		function_list = final_list
		if (len(local_list)!=0):# & (len(function_list)!=0):
			for i in local_list:
				function_list.append(i)
				print("funciones:",function_list)
				time.sleep(5)
		final_list = []
		print(du_index)
		try:
			matrix[0][du_index] = function_list
		except:
			matrix[0].append(function_list)
		du_index +=1
		print("function_list",function_list)
	print("default_list",default_list)
	#translate first row of matrix into the new dus
	to_delete = []
	for i in matrix[0]:
		if i == []:
			#matrix[0].remove(i)
			to_delete.append(i)
		print("hola,",i)
	print(to_delete)
	if len(to_delete)!=0:
		for i in to_delete:
			matrix[0].remove(i)
	if len(default_list)!=0:
		matrix[0].append(default_list)
	matrix[0].insert(0,'Matrix')
	#for i in matrix[0]:
	#	if i == []:
	#		matrix[0].remove(i)
	print("matrix 0:",matrix[0])
	#TODO:make the database coherent to the matrix
	ocuppied_du = []
	cursor = con.cursor()
	for i in matrix[0]:
		if i == 'Matrix':
			continue
		print(i[0])
		#print("Para las funciones",i)
		query="SELECT DU from FUNCTIONS where ORIG_NAME=="+"'"+i[0]+"'"
		cursor.execute(query)
		du_number = cursor.fetchone()[0]
		du_name = "du_"+str(du_number)#(cursor.fetchone()[0])
		#print("\tThe du_name will be: ", du_name)
		while du_number in ocuppied_du: #check until there is no repeated number
			du_number += 1
			du_name = "du_"+str(du_number)
		#print("\tThe du_name will be: ", du_name)
		ocuppied_du.append(du_number)
		#Update ud for all functions indu
		cursor2 = con.cursor()
		lista_fun_aux = i
		#print("la lista es: ", lista_fun_aux)
		if isinstance(lista_fun_aux, list) == False:
			lista_fun_aux = lista_fun_aux.split()
		for j in lista_fun_aux:
			#print("Actualizo",j, "respecto a", lista_fun_aux)
			cursor2.execute("UPDATE functions SET DU = '"+str(du_number)+"' WHERE ORIG_NAME =='"+j+"'")
	#showTables(con)


def make_du0_dependable(config_dict):
	'''this function is for centralize important functions into du_0'''
	print(">>> ENTER IN make_du0_dependable function")
	matrix = config_dict["matrix_filled"]
	function_list = matrix[0][1] #functions belonging to du_0
	#remove parallel, recursive and local
	#if the function list is only one function as a string, convert into list
	if isinstance(function_list, list) == False:
		function_list = function_list.split()
	print("Du_0 functions",function_list)
	print("Config labels",config_dict["labels"])
	du0_functions = []
	print(len(function_list))
	for i in function_list:
		if i in config_dict["labels"]: #remove local, recursive and parallel functions
			if ((config_dict["labels"][i] == 'LOCAL') or (config_dict["labels"][i] == 'RECURSIVE') or (config_dict["labels"][i] == 'PARALLEL')):
				pass
			else:
				du0_functions.append(i) #Other labels not implemented yet	
		else:
			du0_functions.append(i)
	print("Du_0 functions after removal",du0_functions)

	#recollect global
	num_cols=len(matrix[0])
	for i in range(1,num_cols):
		aux_list = matrix[0][i]
		new_list = []
		if isinstance(matrix[0][i], list) == False:
			aux_list = aux_list.split()
		for j in aux_list: #Lo comentado con doble # es para meter las funciones normales en la du_0
			##if its global or normal function goes to du_0, if its labelled goes to the du
			if ("_VAR_" in j) or (j not in config_dict["labels"]):
				du0_functions.append(j)
			##if ((config_dict["labels"][j] == 'LOCAL') or (config_dict["labels"][j] == 'RECURSIVE') or (config_dict["labels"][j] == 'PARALLEL')):
				##new_list.append(j)
			else:
				new_list.append(j)
				##du0_functions.append(j)
		matrix[0][i] = new_list
	#remove repeated elements
	##du0_functions = list(dict.fromkeys(du0_functions))
	du0_functions = list(set(du0_functions))
	#add global functions to du_0
	matrix[0][1] = du0_functions

	#update tables
	con = config_dict["con"]
	cursor = con.cursor()
	
	#make global vars belong to ud 0
	cursor.execute("SELECT ORIG_NAME FROM functions")
	for i in cursor:
		if ("_VAR_" in i[0]) or (j not in config_dict["labels"]):
			cursor2 = con.cursor()
			cursor2.execute("UPDATE functions SET DU = 0 WHERE ORIG_NAME =='"+i[0]+"'")
		#Lo comentado con doble # es para meter las funciones normales en la du_0
		##if i[0] not in config_dict["labels"]:
			##cursor2 = con.cursor()
			##cursor2.execute("UPDATE functions SET DU = 0 WHERE ORIG_NAME =='"+i[0]+"'")
	#showTables(con)

	#Eliminate empty lists from matrix
	aux_matrix = []
	for i in matrix[0]:
		#print("i y tipo", i, type(i))
		if len(i) == 0:
			continue
			#matrix[0].remove(i)
		aux_matrix.append(i)
	matrix[0] = aux_matrix
	print("matrix",matrix[0])

	print(">>> EXIT FROM make_du0_dependable function")

def add_du0_functions(config_dict):
	'''this functions adds labeled functions into du_0'''
	print(">>> ENTER IN add_du0_functions function")
	#miro si no estan ya en la du0
	matrix = config_dict["matrix_filled"]
	function_list = matrix[0][1] #functions belonging to du_0
	con = config_dict["con"]
	cursor = con.cursor()
	du0_candidates = config_dict["du0_functions"]
	#if du0 candidates already are un du0 not taken into account
	for i in du0_candidates:
		if i in function_list:
			du0_candidates.remove(i)
	#updateu su du en sqlite, y las anado a la matriz en du0
	to_delete = ''
	for i in du0_candidates:
		#Las elimino de su du
		for j in matrix[0]:
			if i in j:
				j.remove(i)
				if len(j) == 0:
					to_delete=j# Marco esa du para borrar, porque su unica funcion se ha ido y se ha quedado vacia
		if to_delete != '':
			matrix[0].remove(to_delete)
			to_delete = ''
		function_list.append(i)
		cursor.execute("UPDATE functions SET DU = 0 WHERE ORIG_NAME =='"+i+"'")
	print(">>> EXIT FROM add_du0_functions function")

def showTables(con):
	'''This function is used for get information of the sqlite tables involved'''
	cursor = con.cursor()
	cursor.execute("SELECT * FROM functions")
	print ('\nlets check the table FUNCTIONS\n')
	for i in cursor:
	    print ("ORIG_NAME =",i[0])
	    print ("FINAL_NAME =",i[1])
	    print ("UD =",i[2],"\n")
	print("=============================\n")
	cursor.execute("SELECT * FROM MODULES")
	print ('lets check the table MODULES\n')
	for i in cursor:
	    print ("ORIG_NAME =",i[0])
	    print ("IMPORTS =",i[1])
	    print ("FINAL IMPORT =",i[2],"\n")

def update_du0_functions(config_dict):
	'''this functions updates data base to du0'''
	print(">>> ENTER IN update_du0_functions function")
	matrix = config_dict["matrix_filled"]
	function_list = matrix[0][1] #functions belonging to du_0
	con = config_dict["con"]
	cursor = con.cursor()
	for i in function_list:
		cursor.execute("UPDATE functions SET DU = 0 WHERE ORIG_NAME =='"+i+"'")
	print(">>> EXIT FROM update_du0_functions function")