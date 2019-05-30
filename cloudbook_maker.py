from __future__ import print_function
from graph_analyzer import graph_analyzer
from splitter import splitter
import sqlite3
import logging
import json
from random import randint
import os
import platform

#logging.basicConfig(filename='cloudbook_maker.log',level=logging.DEBUG)
#logging.info('\nThis is the logfile for the cloudbook maker\n')


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

def print_matrix(matrix):
	num_cols=len(matrix[0])
	num_rows=len(matrix)
	for i in range(0,num_rows):
		print (matrix[i])

def load_dictionary(filename):
	'''This function is used for getting the info coming from de config file'''
	with open(filename, 'r') as file:
		aux = json.load(file)
	return aux

#input_dict = load_dictionary("./config_maker.json")

'''if input_dict["circle_info"]["DISTRIBUTED_FS"] == "":
	if(platform.system()=="Windows"):
	    path= os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']+"/cloudbook/"
	    if not os.path.exists(path):
	        os.makedirs(path)
	else:
	    path = "/etc/cloudbook/"
	    if not os.path.exists(path):
	        os.makedirs(path)
else:
	path = input_dict["circle_info"]["DISTRIBUTED_FS"] '''

if(platform.system()=="Windows"):
    path= os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']+"/cloudbook/"
    if not os.path.exists(path):
        os.makedirs(path)
else:
    path = "/etc/cloudbook/"
    if not os.path.exists(path):
        os.makedirs(path)

input_dict = load_dictionary(path+os.sep+"config"+os.sep+"config.json")   

distributed_fs = path#input_dict["circle_info"]["DISTRIBUTED_FS"]
#input_dir = input_dict["input_folder"]
#output_dir = input_dict["output_folder"]
desired_num_dus = input_dict["circle_info"]["NUM_ATTACHED_AGENTS"]

config_dict = {"input_dir": None,
			"output_dir": None,
			"con":None,
			"distributed_fs": None,
			"matrix_info": None,#matrix information at every step, all matrix elements can be resumed in one
			#matrix_info[0]:dirs and files dict, matrix_info[1]: function list
			"matrix_data": None, #matrix filled
			"matrix_filled": None, #matrix filled for internal operations (fill and clean)
			"num_dus": None,
			"labels":None} 

config_dict["distributed_fs"] = distributed_fs
config_dict["input_dir"] = distributed_fs + os.sep + "original"
config_dict["output_dir"] = distributed_fs + os.sep + "distributed" + os.sep + "du_files"
#For testing purposes
#config_dict["input_dir"] = input_dir
#config_dict["output_dir"] = output_dir
config_dict["num_dus"] = desired_num_dus

con = sqlite3.connect(':memory:') #if it is in memory there is no need to delete the databases 
config_dict["con"] = con

#matrix = graph_analyzer.graph_builder(config_dict)
config_dict["matrix_data"] = graph_analyzer.graph_builder(config_dict)
#print_matrix(config_dict["matrix_data"])
matrix = config_dict["matrix_data"]
#print_matrix(matrix)
print("============================",config_dict["labels"])

du_list = splitter.split_program(config_dict)

#Creation of du_dict with du info
#Comentado para probar el parser nuevo
du_dict={}
for i in range(len(du_list)):
	#function_list=final_matrix[0][i]
	#cursor.execute("SELECT DU from FUNCTIONS where ORIG_NAME=="+"'"+function_list[0]+"'")
	du_name = du_list[i]
	du_dict[du_name]={}
	du_dict[du_name]["cost"]=100
	du_dict[du_name]["size"]=100
print(du_dict)

json_str = json.dumps(du_dict)
#fo = open("./du_list.json", 'w')
du_list_route = distributed_fs + os.sep + "distributed"+os.sep+"du_list.json"
fo = open(du_list_route, 'w')
fo.write(json_str)
fo.close()

showTables(con)
