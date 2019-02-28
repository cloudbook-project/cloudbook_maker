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
	flatter.flatten_program(config_dict)
	##Solo hago hasta el flatter
	config_dict["matrix_filled"] = parser.function_parser(config_dict)
	config_dict["matrix_filled"] = matrix_cleaner.clean_matrix(config_dict)
	return config_dict["matrix_filled"]