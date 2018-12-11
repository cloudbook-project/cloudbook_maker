
def clean_matrix(config_dict):
	con = config_dict["con"]
	matrix = config_dict["matrix_filled"]
	clean=False
	while (clean==False):
		num_cols=len(matrix[0])
		num_rows=len(matrix)
		row_to_clean=-1
		#print ("cleaning matrix... rows=",num_rows)
		#print_matrix(matrix)

		for i in range(num_rows-1,1,-1):
			sum=0
			for j in range(1,num_cols):
				sum+=matrix[i][j]

			if (sum==0):
				row_to_clean=i
				break

		#print ("row to clean: ",row_to_clean)

		if row_to_clean==-1 or row_to_clean==1: # main is row 1
			clean=True

		else:
			remove_function_and_DU(con, matrix[i][0]) # must be done before update matrix
			matrix =remove_row(matrix, row_to_clean)
			row_to_clean=-1
			
		

	return matrix

def remove_row(matrix, row_to_clean):
	#print "cleaning row ", row_to_clean
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	matrix_new2= [[None] * (num_cols-1) for i in range(num_rows-1)]
	row2=0
	col2=0
	for i in range(0,num_rows):
		if (i==row_to_clean):
			continue
		for j in range(0,num_cols):
			if (j==row_to_clean):
				continue
			matrix_new2[row2][col2]=matrix[i][j]
			col2+=1
		row2+=1
		col2=0

	matrix=matrix_new2
	##print_matrix(matrix)
	return matrix

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])

def remove_function_and_DU(con,function_name):

	#lets proceed with table FUNCTIONS
	#----------------------------------
	cursor = con.cursor()
	#print "antes:"
	cursor.execute("SELECT ORIG_NAME,DU FROM FUNCTIONS")
	for i in cursor:
	    #print i[0]
	    if function_name==i[0]:
	    	du_delete=i[1]
	    	#print "funcion encontrada!", str(du_delete)
	    	remove_du(con, du_delete)

	cursor.execute("delete from FUNCTIONS where ORIG_NAME ='"+function_name+"'")
	#print "despues:"

	cursor.execute("SELECT ORIG_NAME FROM FUNCTIONS")
	#for i in cursor:
	#    print i[0]
	

def remove_du(con, du):
	cursor=con.cursor()
	cursor.execute("SELECT ORIG_NAME,FINAL_IMPORTS from MODULES")
	imports_list=[]
	imports_list2=[]
	for row in cursor:
		#print "before:-->", row[1]
		
		#print "buscando...."+'"import du_'+str(du)+'",'
		imports_list=row[1].replace("import du_"+str(du),"")
		imports_list2=imports_list.replace(', ""', "")
		#print "after:-->", imports_list2
		cursor2=con.cursor()
		#print "UPDATE MODULES SET FINAL_IMPORTS ='"+ imports_list2+ "' WHERE ORIG_NAME='"+row[0]+"'"
		cursor2.execute("UPDATE MODULES SET FINAL_IMPORTS ='"+ imports_list2+ "' WHERE ORIG_NAME='"+row[0]+"'")
