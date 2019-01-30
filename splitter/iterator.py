#iterates over the functions matrix
import collapser
import collapser_selector
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


#def iterate(con,matrix,desired_num_du):
def iterate(config_dict):
	print (">>>ENTER in iterate()...")
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
	con=config_dict["con"]
	matrix=config_dict["matrix_data"]
	desired_num_du=config_dict["num_dus"]


	num_du= len(matrix[0])-1

	len_collapsable=2 #initially nothing is collapsed. At this point 2 funcs are collapsable
	while(num_du>desired_num_du):
		
		
		collapser_function=collapser_selector.get_collapser(0);

		(f2_col,f1_col)= collapser_function(matrix)
		f2_row=f2_col
		f1_row=f1_col
		#len_collapsable =len(matrix[0][f1_col])
			
		if (f2_row==0 and f1_col==0):
			#print "not possible to collapse more"
			return matrix

		#print "collapsing functions..."
		matrix=collapser.collapse(matrix,f1_row,f2_row, con)

		num_du= len(matrix)-1

		#print "matrix:"
		#print_matrix(matrix_new2)
		
	print (">>>EXIT from iterate()...")
	return matrix

	#return iterate_fake(con,matrix,desired_num_du)


def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])


