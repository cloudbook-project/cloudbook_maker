#gets in every function and get functions calls.

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

def function_parser(function_list):
	#create empty matrix
	matrix = create_matrix(function_list)
	for i in range(len(function_list)+1):
		print matrix[i]
	#fake filled of matrix for testing purposes
	fill_fake(matrix)

def fill_fake(matrix):
	matrix[2][1] = 1 #main calls f1
	matrix[4][1] = 1 #main calls f3
	matrix[3][2] = 10 #f1 calls f2
	print "\n"
	for i in range(len(matrix[0])):
		print matrix[i]
