#gets in every function and get functions calls.
import cloudbook_parser

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

def function_parser(config_dict):
	con = config_dict["con"]
	function_list = config_dict["matrix_info"][1]
	input_path = config_dict["input_dir"]
	matrix = create_matrix(function_list)
	print("=====================PARSER====================")
	print(input_path)
	print("Hay ",len(function_list),"funciones: ",function_list)
	print("Sacamos los ficheros que tenemos que buscar")
	function_path_list=[]
	token_list = {} #dictionary files: tokens
	#get files of the functions and the token for each file
	for i in function_list:
		function_name = i[i.rfind('.')+1:]
		module = i[:i.rfind('.')]
		function_path = input_path+"/"+module.replace('.','/')+".py"
		print("funcion: "+function_name+" modulo: "+module+ " path: "+function_path)
		if function_path not in function_path_list:
			function_path_list.append(function_path)
			#get tokens of file
			#token_list+=cloudbook_parser.tokenize(function_path)
			token_list[module] = cloudbook_parser.tokenize(function_path)
	print("ficheros a buscar",function_path_list)
	print("tokens encontrados", token_list)
	#print_matrix(cloudbook_parser.function_parser(token_list,function_list))
	matrix = cloudbook_parser.function_parser(token_list,function_list)
	return matrix



def function_parser_old(con,input_path,function_list):
	#create empty matrix
	matrix = create_matrix(function_list)
	matrix_test = create_matrix(function_list)
	token_list = []
	#fake filled of matrix for testing purposes
	print("=====================PARSER====================")
	print(input_path)
	#get number of functions
	print("Hay ",len(function_list),"funciones: ",function_list)
	fun_number = 0 #for accessing later the matrix
	for num,i in enumerate(function_list):
		print("La funcion ",num," es ",i)
		function_name = i[i.rfind('.')+1:]
		print("Nombre de funcion",function_name,"con indice",num)
		#convert name function to path
		module = i[:i.rfind('.')]
		print("module",module)
		function_path = input_path+"/"+module.replace('.','/')+".py"
		print("Nombre de fichero",function_path)
		token_list+=cloudbook_parser.tokenize(function_path)
		#cloudbook_parser.function_parser(function_path)
		#for every function open the file and work with it
		'''with open(function_path,'r') as fi:
			isfun = False
			isloop = False
			loop_st = "" #loop statements
			looptabs = 0	#number of tabs to recognize the current loop
			tabs = 0
			for j,line in enumerate(fi,1):
				tabs += line.count('\t')
				if ("def "+ function_name) in line:
					print "Encontrada funcion en linea",j
					#tabs_fun = tabs
					isfun = True
					continue
				if (isfun):
					if ("def ") in line:
						isfun=False
					else:
						print "linea: ",line.replace("\t","")
						if (isloop) and (tabs != looptabs+1):#check if the loop es terminated
							isloop = False
							loop_st = ""
						if "for " in line:#since this line it will be considered that we are inside the loop
							looptabs += tabs+1
							isloop = True
							loop_st = line
						#this line belongs to the function look for other function call
						#evaluation is a tuple of (value,index of function_invoked)
						evaluation = evaluate_line(function_name,line,function_list,isloop,loop_st) #checks if function name call another function
						if evaluation[0] is not 0:
							print "En el indice ",num+1,",",evaluation[1]+1," Voy a poner: ", evaluation[0]
							#matrix_test[num+1][evaluation[1]+1] = evaluation[0]
							matrix_test[evaluation[1]+1][num+1] = evaluation[0]
	fun_number+=1
	#showTables(con)
	fill_fake(matrix)
	print_matrix(matrix_test)
	print "======Matrix comparation========"
	print_matrix(matrix)
	return matrix_test'''
	return cloudbook_parser.function_parser(token_list)

def fill_fake(matrix):
	matrix[2][1] = 1 #main calls f1
	matrix[4][1] = 1 #main calls f3
	matrix[3][2] = 10 #f1 calls f2
	#print "\n"
	#for i in range(len(matrix[0])):
		#print matrix[i]

def evaluate_line(fname,line,flist,isloop,loop_st): #dont get repeated function names
	print("\tEntering in evaluate line")
	print("\t isloop=",isloop)
	value = 0
	fun_number=0
	for num,i in enumerate(flist):
		looked_function = i[i.rfind('.')+1:]
		if looked_function in line:
			print("\t Funcion encontrada:",looked_function,"con indice,",num)
			if (isloop == True):
				print("\t ojo, es un bucle for")
				#indexes for evaluation
				left = loop_st.find("in") +2
				right = len(loop_st)-2
				print("\tEvaluo: ",loop_st[left:right])
				value = len(eval(loop_st[left:right]))
			#elif "while " in line:
			#	pass
			else:
				print("\t le asignare un uno")
				value = 1
			#fun_number += 1
			fun_number = num
	print("\ttupla: ",value,fun_number)
	return (value,fun_number)

def showTables(con):
	#Check Results
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

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])