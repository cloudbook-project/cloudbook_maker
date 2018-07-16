import ud1

def average_0(a,b):
	return (a*b)**1/2
	
def average_1(a,b):
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

print average_0(2,2)
print average_1(2,2)
print ud1.sub(3,2)