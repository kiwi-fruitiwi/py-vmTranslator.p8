# there are no arguments for not; push(!pop)
import enum


# enumeration for our equality helper function which creates asm for eq, lt, gt
class EqualityType(enum.Enum):
    EQ = 1
    LT = 2
    GT = 3


"""
lecture notes
return
    keep track of last function name n
    loop to pop n values off the caller's stack
    replace with callee's stack[0]
    → pseudocode
        endFrame = LCL
        retAddr = *(eF-5)
        *ARG = pop() ← put return value into arg0. part of our contract
        SP = ARG+1
        LCL = *(eF-4)
        ARG = *(eF-3)
        THIS = *(eF-2)
        THAT = *(eF-1)
        goto retAddr

function → always follows call
follows form: function factorial(nVars) ← local variables
    → extract the n and functionName using () and parser.arg1
        print this out to confirm
    → create label, then loop to push 0
        f'({functionName})'  # label        
        
        repeat between 1 and n times: if n=0, do it once
            @SP
            A=M     # select value at SP
            M=0     # set top of stack to 0
            @SP     # increment SP
            M=M+1
                  
        this is my pushConstant code
            'D=A',  # load value of i into register D
            '@SP',
            'A=M',

            'M=D',
            '@SP',
            'M=M+1'
    
    (functionName)
    repeat 'push 0' nVars times, but always push one if nVars is 0
    
call
    push retAddr
    push LCL
    push ARG
    push THIS
    push THAT
    ARG = SP - 5 - nArgs
    LCL = SP
    goto functionName
    (retAddr) ← set label for goto later :3 how to name this? 
        fileName.functionName?    
"""


class CodeWriter:
    """
    invoked with a VM command, .e.g 'push static 5' or 'add', to return a
    List[str] of Hack assembly commands that implement the VM command.
    """

    def __init__(self, filename):
        self.output = open(filename, 'w')
        self.equalityCounter = 0

    # noinspection PyMethodMayBeStatic
    def writeCall(self, command: str) -> [str]:
        return [
            '// [ VM COMMAND ] ' + command,
        ]

    # noinspection PyMethodMayBeStatic
    def writeReturn(self, command: str) -> [str]:
        return [
            '// [ VM COMMAND ] ' + command,
        ]

    # noinspection PyMethodMayBeStatic
    def writeFunction(self, command: str) -> [str]:
        return [
            '// [ VM COMMAND ] ' + command,
        ]

    # noinspection PyMethodMayBeStatic
    def writeLabel(self, command: str, label: str) -> [str]:
        return [  # hackAssembler handles labels on its 1st pass
            '// [ VM COMMAND ] ' + command,
            f'({label})'
        ]

    # noinspection PyMethodMayBeStatic
    def writeGotoLabel(self, command: str, label: str) -> [str]:
        return [
            '// [ VM COMMAND ] ' + command,
            f'@{label}',
            '0;JMP'         # unconditional jump to specified label
        ]

    # noinspection PyMethodMayBeStatic
    def writeIfGotoLabel(self, command: str, label: str) -> [str]:
        return [  # hackAssembler handles labels on its 1st pass
            '// [ VM COMMAND ] ' + command,
            '@SP',
            'AM=M-1',       # select *[SP-1]
            'D=M',
            f'@{label}',   # TODO add function name once we have multiple files
            'D;JNE'        # we just if *[SP-1] is true; note 0 is false
        ]

    # writes to output file the asm commands that implement the vm command given
    def writeArithmetic(self, command) -> [str]:  # List[str] requires import
        # remember to add comments to each command!
        # arith = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

        # print(f'{command}→{command.split()[0]}')
        result = []
        match command.split()[0]:
            case 'neg':
                result = self.__writeNeg()
            case 'add':
                result = self.__writeAdd()
            case 'sub':
                result = self.__writeSub()
            case 'eq':
                result = self.__writeEq()
            case 'lt':
                result = self.__writeLt()
            case 'gt':
                result = self.__writeGt()
            case 'not':
                result = self.__writeNot()
            case 'and':
                result = self.__writeAnd()
            case 'or':
                result = self.__writeOr()
            case _:
                print(f'command not found: {command}')

        self.writelines(result)

    def writePushPop(self, command: str, segment: str, n: int) -> [str]:
        """
        remember to add comments to each command!
        pseudocode: all commands in format of push/pop segName i
            grab arg1 = seg, arg2 = i
            segment names need to be parsed and replaced with their values
                0   SP→256
                1   LCL
                2   ARG
                3   THIS
                4   THAT
                5   TEMP ← needs special case
                16  STATIC ← needs special case

                CONSTANT is only virtual
        """

        result = []
        segDict = {
            'SP': 0,
            'local': 1,
            'argument': 2,
            'this': 3,
            'that': 4,
            'temp': 5,
            'static': 16
        }

        match command.split()[0]:  # push or pop
            case 'pop':
                if segment == 'temp':
                    result = self.__writePopTemp(command, n)
                elif segment == 'pointer':
                    result = self.__writePopPointer(command, n)
                elif segment == 'static':
                    result = self.__writePopStatic(command, n)
                else:
                    result = self.__writePopLATT(command, segDict[segment], n)
            case 'push':
                # take care of push constant i
                if segment == 'constant':
                    result = self.__writePushConstant(command, n)
                elif segment == 'temp':
                    result = self.__writePushTemp(command, n)
                elif segment == 'pointer':
                    result = self.__writePushPointer(command, n)
                elif segment == 'static':
                    result = self.__writePushStatic(command, n)
                else:
                    result = self.__writePushLATT(command, segDict[segment], n)
            case _:
                raise ValueError(f'{command} is not valid in writePushPop')

        self.writelines(result)

    # noinspection PyMethodMayBeStatic
    def __writeEq(self) -> [str]:
        return self.__equalityHelper('EQ')

    # noinspection PyMethodMayBeStatic
    def __writeLt(self) -> [str]:
        return self.__equalityHelper('LT')

    # noinspection PyMethodMayBeStatic
    def __writeGt(self) -> [str]:
        return self.__equalityHelper('GT')

    # noinspection PyMethodMayBeStatic
    def __equalityHelper(self, equalityType: str) -> [str]:
        """
        :return: list of assembly instructions equivalent to one of the three
        equality vm commands, eq, lt, gt
        """

        self.equalityCounter += 1  # we need unique labels in asm
        n = str(self.equalityCounter)

        # flow of this command:
        # check equality of top to elements of the stack
        #   if they are equal, set *(SP-2) to true, SP++
        #   if they aren't, set *(SP-2) to false, SP++
        #

        # below, when SP-1 or SP-2 are mentioned, they refer to the top and 2nd
        # values of the stack, where SP-1 is the top
        return [
            '// [ VM COMMAND ] ' + equalityType,

            # decrement stack pointer. load *(SP-1) → register D
            '@SP',
            'AM=M-1',  # combination of M=M-1, A=M
            'D=M',  # *(SP-1) → register D

            # time to grab *(SP-2)! value of 2nd stack element
            '@SP',
            'AM=M-1',
            'D=M-D',  # store *(SP-2) - *(SP-1) → register D

            # if top two elements of stack are equal, jump!
            #   i.e. if *(SP-1) == *(SP-2), jump
            '@PUSH_TRUE_' + n,  # e.g. @PUSH_TRUE_12
            'D;J' + equalityType,

            # we didn't jump, so top two elements of stack are not equal
            '@SP',
            'A=M',  # *(SP-2) = 0
            'M=0',  # 0 is false because it's 16 0's
            '@SP',  # SP++; stack pointer always points to next available
            # memory location on the stack
            'M=M+1',

            # go to END label; we want to skip the 'they were equal' part below
            '@END' + n,
            'D;JMP',  # D still stores *(SP-2) - *(SP-1)
                      # can optimize to JMP instead of JNE for eq ← cody

            # otherwise the elements were equal!
            '(PUSH_TRUE_' + n + ')',  # if *(SP-1) == *(SP-2)
                                      # *(SP-1)←true
                                      # SP++
            '@SP',  # *(SP-1)←true
            'A=M',
            'M=-1',  # -1 is true because it's 16 1's in two's complement
            '@SP',  # SP++
            'M=M+1',

            '(END' + n + ')'
        ]

    # noinspection PyMethodMayBeStatic
    def __writeOr(self) -> [str]:  # same as 'and' but with one change
        """
        translates a vm 'or' command into its asm equivalent.
        pseudocode:
            a=pop()
            b=pop()
            push(a|b)
        :return:
        """
        return [        # when SP is mentioned, it refers to the original SP
            '// [ VM COMMAND ] or',
            '@SP',      # SP--
            'AM=M-1',
            'D=M',      # D ← RAM[RAM[SP-1]], top of stack
            '@SP',      # SP--
            'AM=M-1',
            'M=D|M',    # RAM[RAM[SP-2]] ← RAM[RAM[SP-1]] | RAM[RAM[SP-2]]
            '@SP',
            'M=M+1'
        ]

    # noinspection PyMethodMayBeStatic
    def __writeAnd(self) -> [str]:
        """
        translates a vm 'and' command into its asm equivalent.
        pseudocode:
            a=pop()
            b=pop()
            push(a&b)
        :return:
        """
        return [        # when SP is mentioned, it refers to the original SP
            '// [ VM COMMAND ] and',
            '@SP',      # SP--
            'AM=M-1',
            'D=M',      # D ← RAM[RAM[SP-1]], top of stack
            '@SP',      # SP--
            'AM=M-1',
            'M=D&M',    # RAM[RAM[SP-2]] ← RAM[RAM[SP-1]] & RAM[RAM[SP-2]]
            '@SP',
            'M=M+1'
        ]

    # noinspection PyMethodMayBeStatic
    def __writeAdd(self) -> [str]:
        return [
            '// [ VM COMMAND ] add',
            '@SP',
            'AM=M-1',   # SP--
            'D=M',      # D ← RAM[ RAM[SP-1] ], top of stack
            '@SP',
            'AM=M-1',
            'M=D+M',
            '@SP',
            'M=M+1'
        ]

    # noinspection PyMethodMayBeStatic
    def __writeSub(self) -> [str]:
        # we always want the deeper stack element to subtract the shallower one
        #   push 5, push 1, sub → 5-1=4
        return [
            '// [ VM COMMAND ] sub',
            '@SP',
            'AM=M-1',
            'D=M',      # D ← RAM[ RAM[SP-1] ], top of stack
            '@SP',
            'AM=M-1',
            'M=M-D',    # RAM[SP-2] - RAM[SP-1]
            '@SP',
            'M=M+1'
        ]

    # noinspection PyMethodMayBeStatic
    def __writeNeg(self) -> [str]:
        return [
            '// [ VM COMMAND ] neg',
            '@SP',
            'A=M-1',
            'M=-M'
        ]

    # noinspection PyMethodMayBeStatic
    def __writeNot(self) -> [str]:
        return [
            '// [ VM COMMAND ] not',
            '@SP',
            'A=M-1',    # shortened from M=M-1; A=M
            'M=!M'      # don't need @SP; M=M+1
        ]

    # noinspection PyMethodMayBeStatic
    def __writePushLATT(self, command: str, seg_location: int, n: int) -> [str]:
        """
        translates a vm 'push segment n' command to its equivalent asm where
        segment is lcl, arg, this, or that. the other 4 segments need special
        handling.
        :param command:
        :param seg_location:
        :param n:
        :return:
        """
        return [
            '// [ VM COMMAND ] ' + command,
            '@'+str(n),
            'D=A',
            '@'+str(seg_location),  # all segments are pointers to some RAM addr
            'D=D+M',    # D=i+RAM[seg]

            '@addr',
            'M=D',      # put RAM[seg]+i into addr variable
            'A=M',
            'D=M',      # D ← RAM[addr] TODO condense +pop

            '@SP',
            'A=M',      # RAM[SP]→A
            'M=D',      # *SP = *addr, i.e. RAM[RAM[SP]]=RAM[addr]

            '@SP',      # SP++
            'M=M+1'
        ]

    # noinspection PyMethodMayBeStatic
    def __writePopLATT(self, command: str, seg_location: int, n: int) -> [str]:
        """
        translates a vm 'pop segment n' command to its equivalent asm where
        segment is lcl, arg, this, or that. the other 4 segments need special
        handling.
        :param command:
        :param seg_location:
        :param n:
        :return:
        """
        return [
            '// [ VM COMMAND ] ' + command,
            '@'+str(n),
            'D=A',
            '@'+str(seg_location),
            'D=D+M',    # D=i+RAM[seg]
            '@popDest',
            'M=D',      # put RAM[seg]+i into popDest variable
            '@SP',
            'M=M-1',    # popping from the stack means decrementing SP
            'A=M',
            'D=M',      # pattern for de-referencing:
                        # equivalent to 'value at this RAM location'
                        # D ← RAM[value of SP]
                        # this is what we are popping
            '@popDest',
            'A=M',      # select RAM[popDest]
            'M=D'       # put popped value into RAM[popDest]
        ]

    # noinspection PyMethodMayBeStatic
    def __writePushStatic(self, command: str, n: int) -> [str]:
        return [
            # push static 5 means push the value of Foo.5 onto the stack
            # 'Foo' is arbitrary, suggested to be the filename. but I'll choose
            # kiwi :p
            '// [ VM COMMAND ] ' + command,
            f'@Kiwi.{str(n)}',  # TODO @Kiwi needs to be filename
            'D=M',  # @Foo.5 stored into register D

            '@SP',
            'A=M',
            'M=D',  # @Foo.5 → *SP

            '@SP',
            'M=M+1'
        ]

    # noinspection PyMethodMayBeStatic
    def __writePopStatic(self, command: str, n: int) -> [str]:
        return [
            # pop static 5 means store *[SP-1] into new variable @Foo.5
            '// [ VM COMMAND ] ' + command,
            '@SP',
            'AM=M-1',
            'D=M',      # D ← top element of stack

            f'@Kiwi.{str(n)}',
            'M=D'
        ]

    # noinspection PyMethodMayBeStatic
    def __writePushPointer(self, command: str, n: int) -> [str]:
        return [
            # given: 'pointer 0' is THIS. 'pointer 1' is THAT. n∈[0,1]
            # conveniently we can use i+3 since THIs is at index 3 while THAT
            # is at index 4
            '// [ VM COMMAND ] ' + command,
            '@'+str(n+3),
            'D=M',      # D ← RAM[i+3]

            '@SP',
            'A=M',
            'M=D',      # RAM[RAM[SP]] ← RAM[i+3]

            '@SP',      # SP++
            'M=M+1',
        ]

    # noinspection PyMethodMayBeStatic
    def __writePopPointer(self, command: str, n: int) -> [str]:
        return [
            # given: 'pointer 0' is THIS. 'pointer 1' is THAT. n∈[0,1]
            # conveniently we can use i+3 since THIs is at index 3 while THAT
            # is at index 4
            '// [ VM COMMAND ] ' + command,
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',  # store *[SP-1] → register D

            '@'+str(n+3),
            'M=D'   # THIS/THAT = *[SP-1]
        ]

    # noinspection PyMethodMayBeStatic
    def __writePushConstant(self, command: str, n: int) -> [str]:
        return [
            '// [ VM COMMAND ] ' + command,

            # *SP=i, SP++
            '@' + str(n),
            'D=A',  # load value of i into register D
            '@SP',
            'A=M',

            'M=D',
            '@SP',
            'M=M+1'
        ]

    # noinspection PyMethodMayBeStatic
    def __writePopTemp(self, command: str, n: int):
        return [
            '// [ VM COMMAND ] ' + command,
            '@' + str(n),
            'D=A',
            '@5',       # pattern for tmp is always i+5
                        # tmp lives in RAM[5-12]
            'D=D+A',    # i+5 → D

            '@addr',
            'M=D',      # put i+5 into addr variable

            '@SP',      # SP--
            'M=M-1',
            'A=M',
            'D=M',      # this is what we are popping

            '@addr',
            'A=M',
            'M=D'       # put popped value into RAM[i+5]
                        # *addr = *SP
        ]

    # noinspection PyMethodMayBeStatic
    def __writePushTemp(self, command: str, n: int):
        return [
            '// [ VM COMMAND ] ' + command,
            '@'+str(n),
            'D=A',
            '@5',       # pattern for tmp is always i+5
                        # tmp lives in RAM[5-12]
            'D=D+A',    # i+5 → D

            'A=D',      # select RAM[i+5]
            'D=M',      # RAM[i+5] → D

            '@SP',
            'A=M',      # RAM[SP]→A
            'M=D',      # *SP = *addr, i.e. RAM[RAM[SP]]=RAM[i+5]

            '@SP',      # SP++
            'M=M+1'
        ]

    def writelines(self, lines: [str]):
        # adds newlines between every entry in lines
        self.output.write('\n'.join(lines) + '\n')

    def close(self):
        self.output.close()
