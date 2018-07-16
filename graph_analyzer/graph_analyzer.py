from matrix_builder import matrix_builder
#from matrix_filler import matrix_filler
from matrix_filler import flatter

import sqlite3

#print matrix_builder.build_matrix(con)
def graph_builder(con):
	result = matrix_builder.build_matrix(con)
	flatter.flatten_program(con,result[1],"../example_program")

