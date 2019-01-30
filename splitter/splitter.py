import iterator
import du_creator

#def split_program(con,matrix,desired_num_deployable_units,input_path,output_path):
def split_program(config_dict):
	con=config_dict["con"]
	matrix=config_dict["matrix_data"]
	input_path=config_dict["input_dir"]
	output_path=config_dict["output_dir"]
	desired_num_deployable_units=config_dict["num_dus"]

	print (">>>ENTER in split_program()...")
	print_matrix(matrix)
	#matrix = iterator.iterate(con,matrix,desired_num_deployable_units)
	matrix = iterator.iterate(config_dict)

	print ("\nTHE COLLAPSED FINAL MATRIX IS:")
	print_matrix(matrix)
	du_list=[]
	du_list = du_creator.create_dus(con,matrix,input_path,output_path)
	#du_list = du_creator.create_dus(config_dict)

	print (">>>EXIT from split_program...")
	return du_list

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])