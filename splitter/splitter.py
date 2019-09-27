import iterator
import du_creator2 as du_creator

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
	add_labeled_functions(config_dict)
	print ("\nTHE COLLAPSED FINAL MATRIX WITH PARALLEL IS:")
	print_matrix(config_dict["matrix_filled"])
	if config_dict["non-reliable_agent_mode"] == True:
		make_du0_dependable(config_dict)
		print ("\nTHE COLLAPSED FINAL MATRIX WITH du_0 du0_dependable IS:")
		print_matrix(config_dict["matrix_filled"])
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
				du0_functions.append(i) #Other labels, not implemented yet	
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
		for j in aux_list: #TODO meter el resto de funciones normales que no le han caido
			if "_VAR_" in j:
				du0_functions.append(j)
			else:
				new_list.append(j)
		matrix[0][i] = new_list
	#add global functions to du_0
	matrix[0][1] = du0_functions

	#update tables
	con = config_dict["con"]
	cursor = con.cursor()
	
	#make global vars belong to ud 0
	cursor.execute("SELECT ORIG_NAME FROM functions")
	for i in cursor:
		if "_VAR_" in i[0]:
			cursor2 = con.cursor()
			cursor2.execute("UPDATE functions SET DU = 0 WHERE ORIG_NAME =='"+i[0]+"'")
	#showTables(con)
	print(">>> EXIT FROM make_du0_dependable function")

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