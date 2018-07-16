import basic

def average(a,b):
	return basic.add(a,b)/2

def mul(a,b):
	aux = a
	for i in range(0,b-1):
		aux = basic.add(aux,a)
	return aux

def fact(a):
	if a==0:
		return 1
	else:
		return mul(a,fact(a-1))

#print mul(2,3)