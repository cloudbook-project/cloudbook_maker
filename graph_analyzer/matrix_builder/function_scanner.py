import os
import logging
import file_scanner
import cloudbook_parser2 as parser
import time

function_names = []

def function_scanner(index):
	pass

def get_functions(files_dict,config_dict):
	print (">>>ENTER in get_functions()...")
	input_folder = str(config_dict["input_dir"])
	#print files_dict

	func_list=[]
	labels_dict = {}
	for dir, files in files_dict.items():
		for f in files: 
			print ("fichero "+f)
			dir2=dir.replace("./","")
			#filename="../example_program_003/input/"+dir+"/"+f
			filename=input_folder+dir2+os.sep+f
			print("=========================================================")
			print(filename)
			tokens = parser.tokenize(filename)
			config_dict["class"] = parser.getClasses(filename)
			config_dict["constants"] = parser.getConstants(tokens)
			print("clases:", config_dict["class"])
			print("constantes", config_dict["constants"])
			print("me da tokens: ")
			for tok in tokens:
				print(str(tok))
			parser.function_scanner(tokens,dir2,f,function_names,labels_dict)
			config_dict["du0_functions"] = parser.getDu0_functions(filename,tokens)
			print("funciones para la du_0",config_dict["du0_functions"])
			#parser.invocation_names(tokens,dir2,f,function_names)#only if necessary, to get the complete names on invocations

	print("functions", function_names)
	print("labels:", labels_dict)
	config_dict["labels"]=labels_dict
	return function_names

	print (">>>EXIT from get_functions()...")
	#int_file = output_path+"/"+du_name+".py"
	#fo = open(output_file, 'w')