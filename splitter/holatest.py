from __future__ import print_function
import logging
logging.basicConfig(filename='example.log',level=logging.DEBUG)
logging.info('\nBienvenido al programa de pruebas\n')

a=10

def cosa():
    """Hola este es el documento
    y voy a meter dos lineas"""
    print ("hola",a)
    print (2.0*4)
    logging.debug("Salimos de la funcion, a vale %d",a)

cosa()
logging.warning('Watch out!')  # will print a message to the console
logging.info('I told you so')  # will not print anything
