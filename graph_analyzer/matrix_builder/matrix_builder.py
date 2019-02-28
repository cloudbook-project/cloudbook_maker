import file_scanner
import function_scanner

import sqlite3 #for testing purposes
import logging

def build_matrix(config_dict):
	#input data (for testing purposes)

	#Files
		#file_main.py  (1 function)
		#dir1/file1.py (2 FUNCTIONS)
		#	 /file2.py (1 function)
		#dir2/file3.py (2function)

	#IMPORTS
		#dir1/file2 => import file1
		#file_main => import dir1.file1
		#			  import dir1.file2
		#			  import dir2.file3

	#Dictionary (clean whithout __init__.py)


	files_dict = {'./': ['file_main.py'],
				'./dir1':['file1.py','file2.py'],
				'./dir2':['file3.py']
				}

	files_dict=file_scanner.file_scanner3(config_dict) # NOT FAKE!!!!
	print ("el escaneo de files es :")
	print (files_dict)
	#List of functions

	function_list=function_scanner.get_functions(files_dict,config_dict)


	#Tables, created in function_list builder, created here for testing purposes
	#con = sqlite3.connect(':memory:') #if it is in memory there is no need to delete the databases 
	con = config_dict["con"]
	cursor = con.cursor()
	cursor.executescript('''
	DROP TABLE IF EXISTS FUNCTIONS;
	DROP TABLE IF EXISTS MODULES;

	CREATE TABLE FUNCTIONS (
	ORIG_NAME TEXT,
	FINAL_NAME TEXT,
	DU INTEGER,
	PRIMARY KEY (ORIG_NAME)
	);

	CREATE TABLE MODULES (
	ORIG_NAME TEXT,
	IMPORTS TEXT,
	FINAL_IMPORTS TEXT,
	PRIMARY KEY (ORIG_NAME)
	)
	''')
	#logging.info('Database connected and tables created')

	#We fill the table as it should be TODO make this with executescript()
	for i in function_list:
		cursor.execute("INSERT INTO FUNCTIONS(ORIG_NAME) VALUES ('"+i+"')")
	'''
	cursor.execute("INSERT INTO FUNCTIONS(ORIG_NAME) VALUES ('file_main.main')")
	cursor.execute("INSERT INTO FUNCTIONS(ORIG_NAME) VALUES ('dir1.file1.fa')")
	cursor.execute("INSERT INTO FUNCTIONS(ORIG_NAME) VALUES ('dir1.file2.fb')")
	cursor.execute("INSERT INTO FUNCTIONS(ORIG_NAME) VALUES ('dir2.file3.fc')")
	cursor.execute("INSERT INTO FUNCTIONS(ORIG_NAME) VALUES ('dir2.file3.fd')")
	cursor.execute("INSERT INTO FUNCTIONS(ORIG_NAME) VALUES ('dir2.file3.fe')")
	'''
	#logging.info('orig names inserted in table "FUNCTIONS"')
	#Check Results
	cursor.execute("SELECT * FROM FUNCTIONS")
	#logging.info('lets check the table')
	#for i in cursor:
	    #logging.info('"ORIG_NAME= ", %s',i[0])

	#Starts with function_list filler
	#logging.info("Lets do flatter")
	#flatter.flatter(cursor,function_list)
	#logging.info("Flatter done, exit")

	#con.close()

	return (files_dict,function_list)