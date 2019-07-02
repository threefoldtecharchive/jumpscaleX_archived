import string 
print "Hello World!\n"


d = {}
val = 1
d['A'] = val
numbers = string.ascii_uppercase
for i in range (2, len(numbers) + 1):
    d[numbers[i-1]] = (i * val) + val
    val = (i * val) + val

#print(d.values())


v = 2
r = ''
n = string.ascii_uppercase
while not v == 0:
    print('aaa')
    for i in range(0, len(n)):
        #print(d[n[i]])
        if v < 3 :
            r = r + 'A'
            v -= 1

print(r)