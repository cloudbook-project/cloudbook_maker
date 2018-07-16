def add(a,b):
	return a+b
def sub(a,b):
	return a-b
def mult(a,b):
	aux = a
	for i in range(0,b-1):
		aux+=a
	return aux

def fact(a):
	if a==0:
		return 1
	else:
		return mult(a,fact(a-1))

a = 5
b = 4

print (add (a,b))
print (sub (a,b))
print (mult (a,b))
print (fact (a))