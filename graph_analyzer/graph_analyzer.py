from matrix_builder import matrix_builder
from matrix_filler import matrix_filler


import sqlite3

#print matrix_builder.build_matrix(con)
def graph_builder(con, input_path):
	matrix_info = matrix_builder.build_matrix(con)
	matrix_data = matrix_filler.fill_matrix(con,matrix_info, input_path)
	return matrix_data

	

