def average(a,b):
	return (a*b)**1/2
	
def average(a,b):
	return add(a,b)/2

def mul(a,b):
	aux = a
	for i in range(0,b-1):
		aux = add(aux,a)
	return aux

def fact(a):
	if a==0:
		return 1
	else:
		return mul(a,fact(a-1))

def add(a,b):
	return a+b