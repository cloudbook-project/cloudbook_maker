
import calculators.calculator1
#import calculators


def get_functions(module):
	print "--------- LIST OF FUNCTIONS AT MODULE " + module +" -------"
	moduledict={}
	#eval( "a =5 ")
	#print a
	moduledict = eval("calculators."+module+".getglobals()")
	for key,val in moduledict.items():
		cosa= (str)(val).find("function "+key)
		if cosa>=0 and key !="getglobals" :
			print key #, val
			
	print "---------------------------------------------------------"		 


#calculators.calculator1.
calculators.calculator1.add(2,3)
#print calculators.calculator1.getlocals()
#print globals()
"""
print "--------- LIST OF FUNCTIONS AT MODULE calculator1 -------"
#print calculators.calculator1.getglobals()
moduledict=calculators.calculator1.getglobals()
for key,val in moduledict.items():
	cosa= (str)(val).find("function "+key)
	if cosa>=0 and key !="getglobals" :
		print key #, val
		
print "---------------------------------------------------------"		 
"""
get_functions("calculator1")
import calculators.calculatorv2