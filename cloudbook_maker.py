from __future__ import print_function
from graph_analyzer import graph_analyzer
from splitter import splitter
import sqlite3
import logging
import json
from random import randint

logging.basicConfig(filename='cloudbook_maker.log',level=logging.DEBUG)
logging.info('\nThis is the logfile for the cloudbook maker\n')


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
	    print ("FINAL IMPORT =",i[2],"\n")


def load_dictionary(filename):
	'''This function is used for getting the info coming from de config file'''
	with open(filename, 'r') as file:
		aux = json.load(file)
	return aux

input_dict = load_dictionary("./config_maker.json")
input_dir = input_dict["input_folder"]
output_dir = input_dict["output_folder"]
desired_num_dus = input_dict["circle_info"]["NUM_ATTACHED_AGENTS"]

config_dict = {"input_dir": None,
			"output_dir": None,
			"con":None,
			"matrix_info": None,#matrix information at every step, all matrix elements can be resumed in one
			#matrix_info[0]:dirs and files dict, matrix_info[1]: function list
			"matrix_data": None, #matrix filled
			"matrix_filled": None, #matrix filled for internal operations (fill and clean)
			"num_dus": None} 

config_dict["input_dir"] = input_dir
config_dict["output_dir"] = output_dir
config_dict["num_dus"] = desired_num_dus

con = sqlite3.connect(':memory:') #if it is in memory there is no need to delete the databases 
config_dict["con"] = con

#matrix = graph_analyzer.graph_builder(config_dict)
config_dict["matrix_data"] = graph_analyzer.graph_builder(config_dict)
matrix = config_dict["matrix_data"]

#du_list = splitter.split_program(con,matrix,2,input_dir,output_dir)
du_list = splitter.split_program(con,matrix,2,input_dir,output_dir)

#Creation of du_dict with du info
du_dict={}
for i in range(len(du_list)):
	#function_list=final_matrix[0][i]
	#cursor.execute("SELECT DU from FUNCTIONS where ORIG_NAME=="+"'"+function_list[0]+"'")
	du_name = du_list[i]
	du_dict[du_name]={}
	du_dict[du_name]["cost"]=randint(1,100)
	du_dict[du_name]["size"]=randint(1,100)
print(du_dict)

json_str = json.dumps(du_dict)
fo = open("./du_list.json", 'w')
fo.write(json_str)
fo.close()

showTables(con)