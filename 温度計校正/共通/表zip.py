# print('dsads' + 'sdaada')

L1 = [1, 2, 3]
L2 = [4, 5, 6]

[print('\t'.join(str(j) for j in i)) for i in zip(L1, L2)]
[print('\t'.join(map(str, 横行))) for 横行 in zip(L1, L2)]
list(map(lambda 横行: print('\t'.join(map(str, 横行))), zip(L1, L2)))

# list(map(lambda x: x, [1, 2, 3]))
