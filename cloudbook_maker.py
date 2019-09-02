from __future__ import print_function
from graph_analyzer import graph_analyzer
from splitter import splitter
import sqlite3
import logging
import json
from random import randint
import os,sys
import platform
from radon.visitors import ComplexityVisitor

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


################################# MAIN ########################################
print (" ")
print (" ")
print ("Welcome to cloudbook maker ")
print ("=====================================")
print ("")
print ("usage")
print ("python cloudbook_maker.py [-matrix <filematrix.json>]")
print ("    ")
print ("    where:")
print ("      -matrix filematrix.json is an optional parameter used for ")
print ("                              remaking a program using new matrix values")
print ("   ")

# gather invocation parameters
# -----------------------------
filematrix=None
num_param=len(sys.argv)
for i in range(1,len(sys.argv)):
	if sys.argv[i]=="-matrix":
		filematrix=sys.argv[i+1]
		i=i+1
#-----------------------------



if(platform.system()=="Windows"):
    path= os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']+"/cloudbook/"
    if not os.path.exists(path):
        os.makedirs(path)
else:
    path = "/etc/cloudbook"
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
			"class":None,
			"constants":None,
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

# in case of remake, we call to graph analyzer but later we overwrite matrix
# it is important call to graph builder in order to update certain config_dict info
config_dict["matrix_data"] = graph_analyzer.graph_builder(config_dict)

if (filematrix !=None):
	print (" USING EXISTING MATRIX: ", filematrix)
	with open(path+"distributed/matrix/"+filematrix, 'r') as file:
		config_dict["matrix_data"] = json.load(file)

#print_matrix(config_dict["matrix_data"])
matrix = config_dict["matrix_data"]
#print_matrix(matrix)
print("============================",config_dict["labels"])

du_list = splitter.split_program(config_dict)

#Creation of du_dict with du info
#Comentado para probar el parser nuevo
du_dict={}

out_route = config_dict["output_dir"] 

for i in range(len(du_list)):
	du_name = du_list[i]
	out_route = config_dict["output_dir"]+os.sep+du_name+".py"
	print (out_route)
	cadena = ""
	file = open(out_route,"r")
	for i in file:
	    cadena = cadena + i	    
	v = ComplexityVisitor.from_code(cadena)
	#print(v.functions)
	temp_complex = 0
	temp_size = 0
	for i in v.functions:
	    #print(i.fullname,i.complexity,i.endline-i.lineno)
	    temp_complex += i.complexity
	    temp_size += i.endline-i.lineno
	du_dict[du_name]={}
	du_dict[du_name]["cost"]=temp_complex
	du_dict[du_name]["size"]=temp_size
	#para el size resto lineas y punto
print(du_dict)

json_str = json.dumps(du_dict)
#fo = open("./du_list.json", 'w')
du_list_route = distributed_fs + os.sep + "distributed"+os.sep+"du_list.json"
fo = open(du_list_route, 'w')
fo.write(json_str)
fo.close()

##showTables(con)
