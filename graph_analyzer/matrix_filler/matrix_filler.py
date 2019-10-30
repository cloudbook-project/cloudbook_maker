#main
import flatter
import sqlite3 #for testing purposes
import logging
import flatter
import parser
import matrix_cleaner

import sys,os
import json
import platform

def showTables(con):
	'''This function is used for get information of the sqlite tables involved'''
	cursor = con.cursor()
	cursor.execute("SELECT * FROM functions")
	print ('\nlets check the table FUNCTIONS\n')
	for i in cursor:
	    print ("ORIG_NAME =",i[0])
	    print ("FINAL_NAME =",i[1])
	    print ("UD =",i[2],"\n")
	print("=============================\n")
	cursor.execute("SELECT * FROM MODULES")
	print ('lets check the table MODULES\n')
	for i in cursor:
	    print ("ORIG_NAME =",i[0])
	    print ("IMPORTS =",i[1])
	    print ("FINAL IMPORTS =",i[2],"\n")


def fill_matrix(config_dict):
	con = config_dict["con"]
	matrix_info = config_dict["matrix_info"]
	input_path = config_dict["input_dir"]
	flatter.flatten_program(config_dict)
	##Solo hago hasta el flatter
	config_dict["matrix_filled"] = parser.function_parser(config_dict)
	config_dict["matrix_filled"] = matrix_cleaner.clean_matrix(config_dict)
	#showTables(config_dict["con"])

	output_dir= config_dict["distributed_fs"]+os.sep+"distributed"+os.sep+"matrix"
	
	#write output file in json format
	#---------------------------------
	json_str = json.dumps(config_dict["matrix_filled"])
	#fo = open("dd", 'w')
	#Create matrix folder
	'''if(platform.system()=="Windows"):
	    path= os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']+"/cloudbook/distributed/matrix"
	    if not os.path.exists(path):
	        os.makedirs(path)
	else:
	    path = os.environ['HOME'] + "/cloudbook/distributed/matrix"
	    if not os.path.exists(path):
	        os.makedirs(path)
	fo = open(output_dir+"/matrix.json", 'w')
	fo.write(json_str)
	fo.close()'''

	return config_dict["matrix_filled"]