def gerar(a, c, m, x):
    return ((a * x + c) % m)

# x = 1
# for i in range(10000):
#     x = gerar(87, 161, 4894967296, x)
#     print(x / 4894967296)