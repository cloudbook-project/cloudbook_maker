from __future__ import print_function
import sqlite3
from graph_analyzer import graph_analyzer
#from splitter import splitter


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
	pass

con = sqlite3.connect(':memory:') #if it is in memory there is no need to delete the databases 

matrix = graph_analyzer.graph_builder(con, "../example_program_001")

#splitter.split_program(con,matrix,2,'../example_program/splitter_output')

showTables(con)