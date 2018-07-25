from matrix_builder import matrix_builder
from matrix_filler import matrix_filler


import sqlite3

#print matrix_builder.build_matrix(con)
def graph_builder(con, input_path):
	print (">>>ENTER in graph_builder()...")
	matrix_info = matrix_builder.build_matrix(con)
	matrix_data = matrix_filler.fill_matrix(con,matrix_info, input_path)
	print (">>>EXIT from graph_builder()...")
	return matrix_data

	

