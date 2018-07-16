#main
import flatter
import sqlite3 #for testing purposes
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p',
                filename='matrix_filler.log',
                filemode='w',
                level=logging.DEBUG)
logging.info('\nThis is the logfile for matrix_filler.py\n')

#input data (for testing purposes)

#Files
	#file_main.py  (1 function)
	#dir1/file1.py (2 functions)
	#	 /file2.py (1 function)
	#dir2/file3.py (2function)

#imports
	#dir1/file2 => import file1
	#file_main => import dir1.file1
	#			  import dir1.file2
	#			  import dir2.file3

#Dictionary (clean whithout __init__.py)
files_dict = {'./': ['file_main.py'],
			'./dir1':['file1.py','file2.py'],
			'./dir2':['file3.py']
			}

#List of functions
matrix = ['file_main.main','dir1.file1.f1','dir1.file1.f2','dir1.file2.f3','dir2.file3.f4','dir2.file3.f5']

#Tables, created in matrix builder, created here for testing purposes
con = sqlite3.connect(':memory:') #if it is in memory there is no need to delete the databases 
cursor = con.cursor()
cursor.executescript('''
DROP TABLE IF EXISTS functions;
DROP TABLE IF EXISTS modules;

CREATE TABLE functions (
orig_name TEXT,
final_name TEXT,
ud INTEGER,
PRIMARY KEY (orig_name)
);

CREATE TABLE modules (
orig_name TEXT,
imports TEXT,
final_imports TEXT,
PRIMARY KEY (orig_name)
)
''')
logging.info('Database connected and tables created')

#We fill the table as it should be TODO make this with executescript()
cursor.execute("INSERT INTO functions(orig_name) VALUES ('file_main.main')")
cursor.execute("INSERT INTO functions(orig_name) VALUES ('dir1.file1.f1')")
cursor.execute("INSERT INTO functions(orig_name) VALUES ('dir1.file1.f2')")
cursor.execute("INSERT INTO functions(orig_name) VALUES ('dir1.file2.f3')")
cursor.execute("INSERT INTO functions(orig_name) VALUES ('dir2.file3.f4')")
cursor.execute("INSERT INTO functions(orig_name) VALUES ('dir2.file3.f5')")

logging.info('orig names inserted in table "functions"')

#Check Results
cursor.execute("SELECT * FROM functions")
logging.info('lets check the table')
for i in cursor:
    logging.info('"ORIG_NAME= ", %s',i[0])

#Starts with matrix filler
logging.info("Lets do flatter")
flatter.flatter(cursor,matrix)
logging.info("Flatter done, exit")

con.close()
