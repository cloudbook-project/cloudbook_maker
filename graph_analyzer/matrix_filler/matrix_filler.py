#main
import flatter
import sqlite3 #for testing purposes
import logging
import flatter
import parser
import matrix_cleaner

def fill_matrix(config_dict):
	con = config_dict["con"]
	matrix_info = config_dict["matrix_info"]
	input_path = config_dict["input_dir"]
	flatter.flatten_program(con,matrix_info[1],input_path)
	matrix_filled = parser.function_parser(con,input_path,matrix_info[1])
	matrix_filled = matrix_cleaner.clean_matrix(con,matrix_filled)
	return matrix_filled