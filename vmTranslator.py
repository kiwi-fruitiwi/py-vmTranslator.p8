"""
@author kiwi 🥝
@date 2022.04.10

⊼².📹 Unit 1.8: VM Translator: Proposed Implementation

parser: parses each vm command into its lexical elements
    ☒ ignores all whitespace, full-line comments, midline comments
    ☒ hasMoreCommands() → boolean
    ☒ advance
    ☒ getCommandType
    ☒ arg1, arg2

codeWriter: writes the assembly code that implements the parsed command
    ☒ opens file in constructor
    ☒ writeArithmetic
    ☒ writePushPop
    ☒ close

main: drives the process. input: fileName.vm, output: fileName.asm
    → iterate through fileName.vm, parse and output with comment
    more routines added in project 8
"""

from codewriter import CodeWriter
from parser import Parser, Command
import os


def main(location: str) -> None:
    # main must determine if filename is directory or file
    # → and instantiate parser objects to read .vm files inside the directory

    # if a file is detected: run process on file
    # if a directory is detected, return list of .vm files; save directory name
    #   → run process on each file in the list and append them

    if os.path.isfile(location):
        print(f'🐳 file detected: {location}')
    elif os.path.isdir(location):
        print(f'[DETECT] directory detected: {location}')
    else:
        raise ValueError(f'{location} does not seem to be a file or directory')

    file = location + 'Sys.vm'
    print(f'🚀 file → {file}')

    parser = Parser(file)
    writer = CodeWriter(location+'NestedCall.asm')

    while parser.hasMoreCommands():
        parser.advance()
        # print(f'{parser.commandType().name}')
        # arith = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        command = parser.command()

        # process each command: is it writeArithmetic or writePushPop?
        match parser.commandType():
            # project 7 commands: memory segments, arithmetic
            case Command.PUSH | Command.POP:
                writer.writePushPop(command, parser.arg1(), int(parser.arg2()))

            case Command.ARITHMETIC:
                writer.writeArithmetic(command)

            # branching commands
            case Command.LABEL:
                writer.writeLabel(command, parser.arg1())

            case Command.IF_GOTO:
                writer.writeIfGotoLabel(command, parser.arg1())

            case Command.GOTO:
                writer.writeGotoLabel(command, parser.arg1())

            # function, call, return
            case Command.FUNCTION:
                writer.writeFunction(command, parser.arg1(), int(parser.arg2()))

            case Command.RETURN:
                writer.writeReturn(command)

            case Command.CALL:
                writer.writeCall(command, parser.arg1(), int(parser.arg2()))

            case _:
                raise ValueError(f'[ ERROR ] command not matched!')

    writer.close()


# main('vm/subTest.vm')
# main('vm/StaticTest.vm')
# main('vm/PointerTest.vm')
# main('vm/BasicTest.vm')

filename = 'C:/Dropbox/code/nand2tetris/kiwi/nand2tetris/projects/08/' \
           'FunctionCalls/NestedCall/'

main(filename)


''' 
notes from lecture

arg1 → string. returns 1st argument of current command
    not called for return
arg2 → int. returns second argument of current command
    only called with push, pop, function, call

commandType → arith, push, pop, label, goto, if, function, ret, call
    commands needed for project 7
        arithmetic+logical: [add sub neg, eq gt lt, and or not]
        memory access: pop segment i, push segment i

    commands needed for project 8
        branching: label, goto, if-goto
        function: function name nVars, call name nArgs, return
'''