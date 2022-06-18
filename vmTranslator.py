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
    ☐ writeArithmetic
    ☐ writePushPop
    ☒ close

main: drives the process. input: fileName.vm, output: fileName.asm
    → iterate through fileName.vm, parse and output with comment
    more routines added in project 8
"""

from codewriter import CodeWriter
from parser import Parser, Command


def main(filename: str) -> None:
    parser = Parser(filename)
    writer = CodeWriter('C:/Dropbox/code/nand2tetris/kiwi/nand2tetris'
                        '/projects/08/FunctionCalls/SimpleFunction'
                        '/SimpleFunction.asm')

    results = []

    while parser.hasMoreCommands():
        parser.advance()
        # print(f'{parser.commandType().name}')
        # arith = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        command = parser.command()

        # process each command: is it writeArithmetic or writePushPop?
        match parser.commandType():
            case Command.PUSH | Command.POP:
                writer.writePushPop(
                    command,
                    parser.arg1(),
                    int(parser.arg2())
                )

            case Command.ARITHMETIC:
                writer.writeArithmetic(command)

            # case Command.C_LABEL | Command.C_IF_GOTO | Command.C_GOTO
            # currently writelines(lines) outputs to file
            #   but writeArithmetic and writePushPop do this inside
            #   themselves instead of returning the list of asm commands.
            #   todo → make this more consistent

            case Command.LABEL:
                writer.writelines(writer.writeLabel(command, parser.arg1()))

            case Command.IF_GOTO:
                writer.writelines(writer.writeIfGotoLabel(command, parser.arg1()))

            case Command.GOTO:
                writer.writelines(writer.writeGotoLabel(command, parser.arg1()))
                print(command)

            case Command.CALL:
                print(f'call command: {command}')

            case Command.FUNCTION:
                writer.writelines(
                    writer.writeFunction(command, parser.arg1(), parser.arg2())
                )

                print(f'function command: {command}')

            case Command.RETURN:
                print(f'return command: {command}')
                writer.writelines(
                    writer.writeReturn(command)
                )

            case Command.CALL:
                print(f'call command {command}')
                writer.writelines(writer.writeCall(command))

            case _:
                print(f'[ ERROR ] command not matched!')

    writer.close()


# main('vm/subTest.vm')
# main('vm/StaticTest.vm')
# main('vm/PointerTest.vm')
# main('vm/BasicTest.vm')
main('vm/SimpleFunction.vm')


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