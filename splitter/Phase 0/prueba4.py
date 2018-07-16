from os import walk, getcwd, path
import re

def ls(regex = '', ruta = getcwd()):
    pat = re.compile(regex, re.I)
    resultado = []
    for (dir, _, archivos) in walk(ruta):
        resultado.extend([ path.join(dir,arch) for arch in 
                              filter(pat.search, archivos) ])
        # break  # habilitar si no se busca en subdirectorios
    return resultado


print(ls( r'-\d+\.[^.\d]*$'))