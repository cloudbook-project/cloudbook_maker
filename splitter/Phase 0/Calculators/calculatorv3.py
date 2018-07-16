def add(a,b):
	return a+b
def sub(a,b):
	return a-b
def mult(a,b):
	aux = a
	for i in range(0,b-1):
		aux+=a
	return aux

a = 5
b = 4

print (add (a,b))
print (sub (a,b))
print (mult (a,b))