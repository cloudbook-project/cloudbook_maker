#iterates over the functions matrix
import collapser
import json


def iterate_fake(con,matrix,num_deployable_units):
	num_cols=6
	num_rows=6
	matrix2 = [[None] * num_cols for i in range(num_rows)]
	matrix2[0] = ['Matrix', 'file_main.main', ['dir1.file1.f1', 'dir1.file1.f2'], 'dir1.file2.f3', 'dir2.file3.f4', 'dir2.file3.f5']
	matrix2[1] = ['file_main.main', 0, 0, 0, 0, 0]
	matrix2[2] = [['dir1.file1.f1', 'dir1.file1.f2'],1,0,0,0,0]
	matrix2[3] = ['dir1.file2.f3',1,0,0,0,0]
	matrix2[4] = ['dir2.file3.f4',0,0,0,0,0]
	matrix2[5] = ['dir2.file3.f5',0,0,0,0,0]

	return matrix2


def iterate(con,matrix,desired_num_du):
	''' this function receives the matrix as input and the number of desired DUs.
		The desired number of DUs will be (normally) the number of available machines.
		Therefore the final number of DUs must be equal or bigger than number of desired DUs.
		Without any iteration, the number of DU is the number of functions.
		The matrix will be colapsed iteratively, reducing the number of DUs, by colapsing the 
		pair of functions which invoke each other more times.
		when the number of DU is equal to number of desired DUs, then the process stops'''

	#first step is to clean matrix. remove functions if they are not invoked
	#matrix=clean_matrix(matrix)
		
	#iteration 0. Num DUs is the number of functions
	#print_matrix(matrix)
	num_du= len(matrix[0])-1
	while(num_du>desired_num_du):
		
		#iteration 1 and next

		#compute the maximum value of matrix to determine which functions to collapse
		#----------------------------------------------------------------------------
		num_cols=len(matrix[0])
		num_rows=len(matrix)
		#print "\n num_cols = ",num_cols, " num_rows = ",num_rows, "\n"
		max_invocations=0
		f1_row=0
		f1_col=0
		f2_row=0
		f2_col=0
		len_collapsable=2 #initially nothing is collapsed

		for i in range(1,num_rows):
			for j in range(1,num_cols):
				# self-invocation is not relevant
				if (i!=j) and (matrix[i][j] >= max_invocations):
					if (matrix[i][j] == max_invocations):
						if (len(matrix[0][j])>len_collapsable):
							continue
					max_invocations=matrix[i][j]
					f2_col=i # f2 invocation column is the row
					f1_col=j # f1 invocation column is the column
					f1_row=f1_col
					f2_row=f2_col
					len_collapsable =len(matrix[0][j])
					
		#print  " max matrix value found =",max_invocations, "at row=",f2_row, " col =", f1_col, "\n"


		if (f2_row==0 and f1_col==0):
			#print "not possible to collapse more"
			return matrix

		#print "collapsing functions..."

		#collapse functions matrix[0][f1_col] and matrix[0][f1_row]
		#----------------------------------------------------------------------------

		matrix_new= [[None] * (num_cols) for i in range(num_rows)]


		#copy matrix
		for i in range(0,num_rows):
			for j in range(0,num_cols):
				if (matrix[i][j]==None) :
					matrix[i][j]=0
				matrix_new[i][j]=matrix[i][j]
		

		#update DU identifier
		#---------------------

		update_DU(con, matrix_new[0][f2_col],matrix_new[0][f1_col])

		#collapse titles
		#-----------------
		#new function is a list of two functions
		matrix_new[0][f1_col] = [matrix_new[0][f1_col],matrix_new[0][f2_col]]
		
		matrix_new[f1_row][0] = matrix_new[0][f1_col] 


		#collapse column and row values
		#------------------------------
		for i in range(1,num_rows):
			for j in range(1,num_cols):

				#when column = f2 column, just update f1+f2 column and set to zero f2 column
				if (j==f1_col):
					matrix_new[i][j]+=matrix[i][f2_col]
					matrix_new[i][f2_col]=0 # now f2 not invoke nothing
				if (i==f2_row):
					matrix_new[f1_row][j]+=matrix[i][j]	
					matrix[i][j]=0	
				
		
		#delete column f2 and row f2
		#----------------------------
		matrix_new2= [[None] * (num_cols-1) for i in range(num_rows-1)]
		row2=0
		col2=0
		for i in range(0,num_rows):
			if (i==f2_row):
				continue
			for j in range(0,num_cols):
				if (j==f2_col):
					continue
				matrix_new2[row2][col2]=matrix_new[i][j]
				col2+=1
			row2+=1
			col2=0

		matrix=matrix_new2
		num_du= len(matrix)-1

		#print "matrix:"
		#print_matrix(matrix_new2)
		

	return matrix

	#return iterate_fake(con,matrix,desired_num_du)


def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])


def update_DU(con, f2_list, f1_list):
	
	#lets proceed with functions table
	#----------------------------------
	list2=[[]]
	list1=[[]]

	

	if isinstance(f2_list, str):
		list2[0]=f2_list
	else:
		list2=f2_list
	if isinstance(f1_list, str):
		list1[0]=f1_list
	else:
		list1=f1_list
	
	cursor = con.cursor()
	cursor.execute("SELECT DU from FUNCTIONS where ORIG_NAME='"+list1[0]+"'")

	#for row in cursor:
	#	du=row[0]
	du=cursor.fetchone()[0]

	cursor.execute("SELECT DU from FUNCTIONS where ORIG_NAME='"+list2[0]+"'")
	du_old=cursor.fetchone()[0]

	for i in list2:
		cursor.execute("UPDATE FUNCTIONS set DU="+str(du)+" where ORIG_NAME='"+i+"'")
	
	#now proceed with modules table
	#--------------------------------
	cursor.execute("SELECT ORIG_NAME,FINAL_IMPORTS from MODULES")
	imports_list=[]
	for row in cursor:
		#print "before:-->", row[1]
		
		imports_list=row[1].replace("import du_"+str(du_old),"import du_"+str(du) )
		#print "after:-->", imports_list
		cursor2=con.cursor()
		#print "UPDATE MODULES SET FINAL_IMPORTS ='"+ imports_list+ "' WHERE ORIG_NAME='"+row[0]+"'"
		cursor2.execute("UPDATE MODULES SET FINAL_IMPORTS ='"+ imports_list+ "' WHERE ORIG_NAME='"+row[0]+"'")
		

	