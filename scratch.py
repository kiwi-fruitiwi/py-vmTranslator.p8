import os


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

# what does range do again? XD
for index in range(4):
    print(index)

# prints files of a certain extension inside a directory
print(os.listdir('.'))
for file in os.listdir('.'):
    if file.lower().endswith('.py'):
        print(file)