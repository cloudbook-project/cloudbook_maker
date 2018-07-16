from __future__ import print_function
import sqlite3
from graph_analyzer import graph_analyzer


def showTables(con):
	#Check Results
	cursor = con.cursor()
	cursor.execute("SELECT * FROM functions")
	print ('lets check the table\n')
	for i in cursor:
	    print ("ORIG_NAME =",i[0])
	    print ("FINAL_NAME =",i[1])
	    print ("UD =",i[2],"\n")

con = sqlite3.connect(':memory:') #if it is in memory there is no need to delete the databases 

graph_analyzer.graph_builder(con)

#showTables(con)