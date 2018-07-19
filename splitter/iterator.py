#iterates over the functions matrix
import collapser

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
	matrix=clean_matrix(matrix)
		
	#iteration 0. Num DUs is the number of functions
	print_matrix(matrix)
	num_du= len(matrix[0])-1
	while(num_du>desired_num_du):
		
		#iteration 1 and next

		#compute the maximum value of matrix to determine which functions to collapse
		#----------------------------------------------------------------------------
		num_cols=len(matrix[0])
		num_rows=len(matrix)
		print "\n num_cols = ",num_cols, " num_rows = ",num_rows, "\n"
		max_invocations=0
		f1_row=0
		f1_col=0
		f2_row=0
		f2_col=0

		for i in range(1,num_rows):
			for j in range(1,num_cols):
				# self-invocation is not relevant
				if (i!=j) and (matrix[i][j] > max_invocations):
					max_invocations=matrix[i][j]
					
					f2_col=i # f2 invocation column is the row
					f1_col=j # f1 invocation column is the column
					f1_row=f1_col
					f2_row=f2_col
					
		print  " max matrix value found =",max_invocations, "at row=",f2_row, " col =", f1_col, "\n"

		if (f2_row==0 and f1_col==0):
			print "not possible to collapse more"
			return matrix


		print "collapsing functions..."

		#collapse functions matrix[0][f1_col] and matrix[0][f1_row]
		#----------------------------------------------------------------------------

		matrix_new= [[None] * (num_cols) for i in range(num_rows)]


		#copy matrix
		for i in range(0,num_rows):
			for j in range(0,num_cols):
				if (matrix[i][j]==None) :
					matrix[i][j]=0
				matrix_new[i][j]=matrix[i][j]
		

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

		print "matrix:"
		print_matrix(matrix_new2)
		

	return matrix

	#return iterate_fake(con,matrix,desired_num_du)


def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])

def clean_matrix(matrix):
	
	clean=False
	while (clean==False):
		num_cols=len(matrix[0])
		num_rows=len(matrix)
		row_to_clean=-1
		print ("cleaning matrix... rows=",num_rows)
		print_matrix(matrix)

		for i in range(1,num_rows):
			sum=0
			for j in range(1,num_cols):
				sum+=matrix[i][j]

			if (sum==0):
				row_to_clean=i

		print ("row to clean: ",row_to_clean)

		if row_to_clean==-1 or row_to_clean==1: # main is row 1
			clean=True

		else:
			matrix =remove_row(matrix, row_to_clean)
			row_to_clean=-1
			
		

	return matrix

def remove_row(matrix, row_to_clean):
	print "cleaning row ", row_to_clean
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
	#print_matrix(matrix)
	return matrix