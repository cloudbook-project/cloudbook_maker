import iterator
import du_creator

def split_program(con,matrix,dsired_num_deployable_units,input_path,output_path):
	matrix = iterator.iterate(con,matrix,dsired_num_deployable_units)
	du_creator.create_dus(con,matrix,input_path,output_path)
