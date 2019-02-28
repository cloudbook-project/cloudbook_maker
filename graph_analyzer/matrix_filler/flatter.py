#flats packages and subpackages, creates new modules and changes invocations
from __future__ import print_function
import sqlite3 
import logging
import json
import cloudbook_parser2 as cloudbook_parser


def flatten_program(config_dict):
	print (">>>ENTER in flatten_program...")
	con = config_dict["con"]
	function_list = config_dict["matrix_info"][1]
	files_path = config_dict["input_dir"]
	#check database and insert ud number DUMB ASIGNATION
	#TODO: Detect ud0 for better assignation. Done in function scanner, already pos 0
	#step1: assign ud's to functions
	cursor = con.cursor()
	#logging.info('FLATTER::inserts ud number')
	for i in range(len(function_list)):
		cursor.execute("UPDATE functions set DU = "+ str(i) + ", FINAL_NAME = 'f"+str(i)+"' WHERE orig_name = '"+function_list[i]+"'")
		# function main is the first position of array function_list and therefore UD-0 is assigned to main
	#step2: check modules and translate imports x to import udx
	modules = []
	for i in function_list:
		j = i.rfind('.')
		module = i[:j]
		if module not in modules:
			modules.append(module)
	#print modules

	#translate import
	#print("Lets translate imports")
	modules_dict = {}
	for i in  modules:
		filename = files_path +"/" + i.replace(".","/")+".py"
		#print("filename: "+ filename)
		modules_dict[filename]=[]
		'''with open(filename, 'r') as f:
			for line in f:
				aux = line.split(' ')
				if aux[0]=='import':
					line = line.replace('\n','')
					modules_dict[filename].append(line)'''
		token_list = cloudbook_parser.tokenize_imports(filename)
		for token in token_list:
			modules_dict[filename].append(token.value)
	#print ("modules dict",modules_dict)
	#select ud from functions where f(orig_name) == filename(without .py)
	ud_modules={}
	#print("=====================================")
	for i in modules_dict:
		ud_modules[i]=[]
		for j in modules_dict[i]:
			#j = import xxxx
			#print("Vamos a traducir ", j)
			module = j.split(" ")[1]#this is the imported module
			#hay que hacer mejor lo del modulo, con ERs
			found = False
			#print("\tsu modulo es ", module)
			cursor.execute("SELECT orig_name,du from functions")
			#print("\tHacemos SELECT orig_name,du from functions")
			for k in cursor:
				#print("\t\tk: ",k)
				index = k[0].rfind('.')
				asoc_module = k[0][:index]
				#print("\t\tasoc_module es ",asoc_module)
				#module package is i
				cosa=i.replace(files_path,"")#replace input dir
				cosa=cosa.replace(".py","")
				cosa=cosa.replace("/",".")
				cosa = cosa[1:(len(cosa)+1)]
				#print "Cosa= ",cosa
				#si no hay punto, como luego hace un find no pasa nada,  pero hay que hacerlo bien
				module_package = cosa[:cosa.rfind('.')]
				#print("\t\tmodule_package es ",module_package, "(sacado de ",i,")")
				#print "module_package= ",module_package
				relative_index= asoc_module.find(module_package)
				if relative_index != -1:
					relative_index+=len(module_package)+1
					#print "relative index= ", relative_index
					asoc_module_relative = asoc_module[relative_index:]
				else:
					asoc_module_relative = ""
				#print ("\t\tabsolute= ", asoc_module)
				#print ("\t\trelative= ", asoc_module_relative)
				#print("\t\tY las cambiamos por su numero de du si es necesario")
				if asoc_module == module or asoc_module_relative==module:
					ud_modules[i].append("import du_" + str(k[1]))
					#print("\t\tappend: ","import du_" + str(k[1]))
					found=True
			if not found:
				#print("\t\tappend: ",j)
				ud_modules[i].append(j)
	#print ud_modules

	######Insert Data into Database########
	for i in modules_dict:
		module_name=i.replace(files_path,"")
		module_name=module_name.replace(".py","")
		module_name=module_name.replace("/",".")
		module_name = module_name[1:(len(module_name)+1)]
		cursor.execute("INSERT INTO MODULES(ORIG_NAME,IMPORTS,FINAL_IMPORTS) VALUES ('"+module_name+"','"+json.dumps(modules_dict[i])+"','"+json.dumps(ud_modules[i])+"')")

	#d(cursor)
	



	

