import iterator
import du_creator

def split_program(con,matrix,desired_num_deployable_units,input_path,output_path):
	matrix = iterator.iterate(con,matrix,desired_num_deployable_units)
	print_matrix(matrix)
	du_creator.create_dus(con,matrix,input_path,output_path)

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])