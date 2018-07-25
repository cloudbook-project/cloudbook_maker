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
	directory="../../../example_program_001/input"
	file_dictionary = {}


	files1=[]
	files2=[]
	files3=[]
	
	#rootDir = '.'
	rootDir = '../../../example_program_001/input'
	for dirName, subdirList, fileList in os.walk(rootDir):
		dirName=dirName.replace(rootDir+"\\","./")
		#print('Found directory: %s' % dirName)
		for fname in fileList:
			#print('\t%s' % fname)
			pass



	for root, dirs, files in os.walk(directory):
		
	
		print files
		files1 = [f for f in files if not f[0] == '.'] #ignore hidden files


		for name in files1:
			if name.find(".pyc")==-1 and name.find(".py")!=-1 and name[0:2].find("__")==-1:
				files2.append(name)

		
		#for name in files2:
		#	files3.append(os.path.join(root, name))
		#dirs[:] = [d for d in dirs if not d[0] == '.'] #ignore hidden dirs

		file_dictionary[root]=files2
    
    #print "=========================== FILE DICT =================================="
	#print file_dictionary      	
	return file_dictionary



def file_scanner2():
	print (">>>ENTER in file_scanner()...")
	directory="../../../example_program_001/input"
	file_dictionary = {}


	files1=[]
	files2=[]
	files3=[]
	dict_files={}
	
	#rootDir = '.'
	rootDir = '../../../example_program_001/input'
	rootDir = '../example_program_001/input'
	for dirName, subdirList, fileList in os.walk(rootDir):
		dirName=dirName.replace(rootDir+"\\","./")
		dirName=dirName.replace(rootDir,"./") # root
		#print('Found directory: %s' % dirName)
		files2=[]
		for fname in fileList:
			#print('\t%s' % fname)
			if fname.find(".pyc")==-1 and fname.find(".py")!=-1 and fname[0:2].find("__")==-1:
				files2.append(fname)
		dict_files[dirName]=files2
	print (">>>EXIT from file_scanner()...")
	return dict_files

if __name__ == "__main__":
	print file_scanner2()