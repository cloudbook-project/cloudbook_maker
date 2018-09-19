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
	#Check Results
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


def remove_output_directory():
	pass


def copy_input_directory():
	#copy and remove comments
	pass

def load_dictionary(filename):
	with open(filename, 'r') as file:
		aux = json.load(file)
	return aux

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])

config_dict = load_dictionary("./config_maker.json")
input_dir = config_dict["input_folder"]
output_dir = config_dict["output_folder"]

con = sqlite3.connect(':memory:') #if it is in memory there is no need to delete the databases 

matrix = graph_analyzer.graph_builder(con, input_dir)

du_list = splitter.split_program(con,matrix,2,input_dir,output_dir)

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