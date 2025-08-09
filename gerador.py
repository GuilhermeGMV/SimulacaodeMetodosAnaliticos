a = 87
c = 161
m = 10003
x = 1

for i in range(1000):
    x = (a * x + c) % m
    print(x)