# extend will extend per-character if you feed it a string
# → enclose strings in a list :p

result: [str] = []
header: [str] = ['// [ VM COMMAND ] call sys.init 0']

nArgsCheck: [str] = [
    '@SP',
    'M=M+1'
]

result.extend(header)
result.extend(nArgsCheck)

print(result)

for index in range(4):
    print(index)