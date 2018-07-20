
def clean_matrix(matrix):
	
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
