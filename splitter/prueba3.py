import os
from os import walk, getcwd, path
import re
from os import listdir
from os.path import isfile, join,isdir

def ls2(ruta = '.'):
	mydict={}	
	lista_files_aux=listdir(ruta)
	lista_files=[]
	mydict[ruta]=[]
	i=0
	#print "--------"
	#print "estamos en ruta "+ ruta
	for arch in lista_files_aux:
		if arch[0]!='.':
			if isfile(ruta+"/"+arch):
				#lista_files.append(arch)
				if arch[0]!='.':
					mydict[ruta].append(arch)
					
			elif isdir(ruta+"/"+arch):
				#print arch + " es un dir"
				a=1
				#mydict[ruta+"/"+arch]= ls2(ruta+"/"+arch)
			#else :
			#	print arch + " es raro"
	return mydict
	
	"""
		if isfile(arch):
			 lista_files.extend(arch)
		else:
			mydict[arch]=lista_files
	"""	
	#return mydict
    #return [arch for arch in listdir(ruta) if isfile(join(ruta, arch))]
    	
    



def ls(regex = '', ruta = getcwd()):
    pat = re.compile(regex, re.I)
    resultados = {}
    for (dir, _, archivos) in walk(ruta):
        #resultado.extend([ path.join(dir,arch) for arch in filter(pat.search, archivos) ])

        resultado=([ path.join(arch) for arch in filter(pat.search, archivos) ])
        #print resultado
        resultados[dir]=resultado
        # break  # habilitar si no se busca en subdirectorios
    return resultados

def prueba():
	directorio="./"
	indice = {}
	for root, dirs, files in os.walk(directorio):
		files = [f for f in files if not f[0] == '.']
		dirs[:] = [d for d in dirs if not d[0] == '.']
		#print "root",root
		#print "dirs",dirs		
		#print "files",files
		indice[root]=files
          	
	print indice


#print(ls('.py'))
#mydict=ls()
#print mydict
print "--------------------------"
print ls2()
print "--------------------------"
prueba()