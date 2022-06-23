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
from pathlib import Path  # used for Path().stem
import os

print('\n\n\n')


# translates vm code to assembly at the specified locations with an option to
# overwrite writeLoc
def translate(readLoc: str, writeLoc: str, overwrite: bool):
    print(f'[ INFO ] translating starting → {readLoc}')

    parser = Parser(readLoc)

    if overwrite:
        writer = CodeWriter(writeLoc, 'w')
    else:
        writer = CodeWriter(writeLoc, 'a')

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
    print(f'[ INFO ] assembly output complete → {writeLoc}')


def main(absPath: str) -> None:
    # main must determine if filename is directory or file
    # → and instantiate parser objects to read .vm files inside the directory

    """
    encapsulate parser writer loop with a single method
    save the directory name

        if a file is detected:
            parser reads loc.vm
            writer outputs to loc.asm
        if directory:
            vmFileList ← generate
                parser reads all .vm files in vmFileList
                while codeWriter writes each one to loc.asm

    :param absPath:
    :return:
    """

    # os.path.abspath returns abspath from where the .py file is executing

    if os.path.isfile(absPath):
        print(f'🐳 file detected: {absPath}')
        # run parser writer loop on the file
        # todo find directory name. or chop off .vm and replace with .asm

        basename = os.path.basename(os.path.dirname(absPath))
        print(f'directory name → {basename}\n')

        stem = Path(absPath).stem  # a stem is a filename without an extension
        print(f'stem → {stem}\n')

        path = Path(absPath)
        parentPath = path.parent.absolute()
        print(f'parent path → {parentPath}')

        # if the path is a file, output asm is the file's name
        translate(absPath,
                  str(parentPath)+stem+".asm",
                  overwrite=True)


    elif os.path.isdir(absPath):
        print(f'[DETECT] directory detected: {absPath}')
        # if the path is a directory, generate list of vm files in directory
        # run parser writer loop on each one; codeWriter uses 'w[rite]' mode at
        # first, then '[a]ppend' mode for subsequent files in the list

        # loop through .vm files in directory
        for file in os.listdir(absPath):
            if file.lower().endswith('.vm'):
                print(f'🚙 looping through vm files → {file}, '
                      f'{os.path.abspath(file)}')
        print('\n')

        # detect .vm files in this directory
        # we should overwrite if this is the first time we're in a directory
        #   but append for all following files

        # save directory root
        root = absPath
        # print(f 'root → {root}')

        # folder name, not path
        basename = os.path.basename(os.path.dirname(absPath))
        # print(f 'dirname → {basename}\n')

        outputPath = root+basename+".asm"
        # print(f 'output path → {outputPath}')

        for file in os.listdir(absPath):
            if file.lower().endswith('.vm'):  # 'file' is a VM file
                readPath = root+file
                # print( f'📃 translating: {readPath}')
                translate(readPath,
                          outputPath,
                          overwrite=False)
    else:
        raise ValueError(f'{absPath} does not seem to be a file or directory')

    # translate(location+'Sys.vm', location+'NestedCall.asm', overwrite=True)


# filename = 'C:/Dropbox/code/nand2tetris/kiwi/nand2tetris/projects/08/' \
#            'FunctionCalls/FibonacciElement/'
#
# filename = 'C:/Dropbox/code/nand2tetris/kiwi/nand2tetris/projects/07/' \
#            'MemoryAccess/BasicTest/BasicTest.vm'

# directories must end with an {os.sep}, which is in this case a '/'
filename = 'C:/Dropbox/code/nand2tetris/kiwi/nand2tetris/projects/07/' \
           'MemoryAccess/StaticTest/'

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
