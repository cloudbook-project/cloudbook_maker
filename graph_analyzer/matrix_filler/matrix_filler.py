#main
import flatter
import sqlite3 #for testing purposes
import logging
import flatter
import parser

def fill_matrix(con,matrix_info):
	flatter.flatten_program(con,matrix_info[1],input_path)
	matrix_filled = parser.function_parser(matrix_info[1])
	return matrix_filled