#main
import flatter
import sqlite3 #for testing purposes
import logging
import flatter
import parser
import matrix_cleaner

def fill_matrix(con,matrix_info, input_path):
	flatter.flatten_program(con,matrix_info[1],input_path)
	matrix_filled = parser.function_parser(matrix_info[1])
	matrix_filled = matrix_cleaner.clean_matrix(matrix_filled)
	return matrix_filled