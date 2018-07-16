import os
import logging

logging.basicConfig(filename='file_scanner.log',level=logging.DEBUG)
logging.info('\nThis is the logfile for files_scanner.py\n')

def file_scanner():
	'''This function generates a dictionary of directories and files
	Example: {
			  name_dir: [file1,...,fileN], 
			  name_dir2: [file1b]
			  }
	'''
	directory="./" #doesnt get directory as parameter
	file_dictionary = {}
	for root, dirs, files in os.walk(directory):
		files = [f for f in files if not f[0] == '.'] #ignore hidden files
		dirs[:] = [d for d in dirs if not d[0] == '.'] #ignore hidden dirs
		file_dictionary[root]=files
          	
	return file_dictionary


if __name__ == "__main__":
	print file_scanner()