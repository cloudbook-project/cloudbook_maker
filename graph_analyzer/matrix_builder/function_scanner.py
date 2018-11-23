import os
import logging
import file_scanner
import cloudbook_parser as parser

function_names = []

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
			tokens = parser.tokenize(filename)
			print("me da tokens: "+ str(tokens))
			parser.function_scanner(tokens,dir2,f,function_names)
			print(function_names)

	print(function_names)
	return function_names

	print (">>>EXIT from get_functions()...")
	#int_file = output_path+"/"+du_name+".py"
	#fo = open(output_file, 'w')