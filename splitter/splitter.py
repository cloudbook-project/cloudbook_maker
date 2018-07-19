import iterator
import du_creator

def split_program(con,matrix,num_deployable_units,output_path):
	matrix = iterator.iterate(con,matrix,num_deployable_units)
	du_creator.create_uds(con,matrix,output_path)
