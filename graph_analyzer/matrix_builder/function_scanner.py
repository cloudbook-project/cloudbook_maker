import os
import logging
import file_scanner

logging.basicConfig(filename='function_scanner.log',level=logging.DEBUG)
logging.info('\nThis is the logfile for function_scanner.py\n')

def function_scanner(index):
	pass



def get_functions(files_dict):
	print (">>>ENTER in get_functions()...")
	#print files_dict

	func_list=[]
	for dir, files in files_dict.items():
		for f in files: 
			print ("fichero "+f)
			dir2=dir.replace("./","")
			filename="../example_program_001/input/"+dir+"/"+f
			fo=open(filename, 'r')

			line=fo.readline()
			while line:
				if line[0:5].find ("def ")!=-1:
					#line.replace("def ","")
					func_name=dir2+"."+f.replace(".py","")+"."+line.replace("def ","")
					func_name=func_name.replace("():","")
					func_name=func_name.replace("\n","")
					print func_name
					func_list.append(func_name)
				line=fo.readline()	
			 
			fo.close()

	print func_list
	return func_list

	print (">>>EXIT from get_functions()...")
	#int_file = output_path+"/"+du_name+".py"
	#fo = open(output_file, 'w')