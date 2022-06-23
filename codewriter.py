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

function: always follows call, in the form of function factorial(nVars)
    nVars specifies number of local variables
    (functionName)
    repeat 'push 0' nVars times
    
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

    def __init__(self, filename: str, writeChar: str):
        self.output = open(filename, writeChar)
        self.equalityCounter = 0
        self.retAddrCounter = 0

    # noinspection PyMethodMayBeStatic
    def writeCall(self, command: str, fName: str, nArgs: int) -> [str]:
        """
        examples: call Sys.add12 1, function Sys.init 0

        pseudocode
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

        if nArgs == 0: # save a spot for argument 0: return address location
            @SP
            M=M+1

        self.retAddrCounter += 1
        → push retAddr: we need a global retAddr counter →📇
            f'@retAddr_{retAddrCounter}'
            D=A     # value of retAddr_n → register D
            @SP
            A=M
            M=D     # pushes retAddr_n onto the stack
            @SP     # increment SP to complete push
            M=M+1

        → push LCL, ARG, THIS, THAT
            memSegs = ['LCL', 'ARG', 'THIS', 'THAT']
            memSegPushCode = [
                D=M     # value of memSeg's location → register D
                @SP
                A=M
                M=D     # *(SP) = memSeg's location
                @SP     # increment SP
                M=M+1
            ]

            loop from 0-3:
            @memSegs[0-3]
            results.extend(memSegPushCode)

        → also consider memSegPushDRegister = results.extend [
                @SP
                A=M
                M=D     # *(SP) = memSeg's location
                @SP     # increment SP
                M=M+1
            ]

        → ARG = SP - 5 - nArgs
            @ there always needs to be one argument slot for the return value
            if nArgs == 0:
                argOffset = 5+1
            else:
                argOffset = 5+nArgs
            @SP
            D=M
            f'@{argOffset}'
            D=D-A       # D ← SP-5-nArgs

            @ARG
            M=D

        → LCL = SP
            @LCL
            D=M
            @SP
            M=D

        → goto functionName
            f'({functionName})'
            0;JMP

        → (retAddr)
            f'(retAddr_{retAddrCounter})'


            if nArgs == 0: # save a spot for argument 0: return address location
            @SP
            M=M+1

        """

        # our code consists of several parts:
        #   save frame: push retAddr, LCL, ARG, THIS, THAT
        #       check if we need to make space for argument 0 if nArgs is 0
        #   set new ARG=SP-5-nArgs
        #   set new LCL=SP
        #   goto functionName
        #   set returnAddress label

        self.retAddrCounter += 1  # unique return address ID for every call
        results: [str] = []  # initialize empty list of asm code
        header: [str] = ['// [ VM COMMAND ] ' + command]

        zeroNArgs: bool = (int(nArgs) == 0)
        # print(f'zeroNArgs→{nArgs}, {zeroNArgs}')
        nArgsCheck: [str] = []

        # if nArgs is zero, we have to make space for the return value in arg0
        if zeroNArgs:
            nArgsCheck = [
                '@SP',
                'M=M+1'
            ]

        # saveFrame: push returnAddress, LCL, ARG, THIS, THAT
        saveFrameMemSegs = ['LCL', 'ARG', 'THIS', 'THAT']
        pushDRegister: [str] = [
            '@SP',
            'A=M',
            'M=D',
            '@SP',
            'M=M+1'
        ]

        # recall how the hackAssembler handles labels and symbols: on its
        # first pass, it will see a (retAddr_n) label deeper in the code and
        # convert it to the numerical value of the next line. then this
        # symbol will be converted to that value on the second pass of the
        # hackAssembler.
        pushRetAddr: [str] = [f'@retAddr_{self.retAddrCounter}', 'D=A']
        pushRetAddr.extend(pushDRegister)

        saveFrame: [str] = []
        saveFrame.extend(pushRetAddr)

        for index in range(4):
            saveFrame.extend([f'@{saveFrameMemSegs[index]}', 'D=M'])
            saveFrame.extend(pushDRegister)

        argOffset: int
        if zeroNArgs:  # todo cody suggests +max(1, nArgs)
            argOffset = 6  # 5 default +1 extra for space we set aside earlier
        else:
            argOffset = 5+int(nArgs)

        setArg: [str] = [  # set ARG = SP-5-nArgs. if nArgs=0, SP-6
            '@SP',
            'D=M',
            f'@{argOffset}',
            'D=D-A',  # D ← SP-5-nArgs or SP-6 if nArgs=0
            '@ARG',
            'M=D'
        ]

        setLcl: [str] = [  # set LCL = SP
            '@SP',
            'D=M',
            '@LCL',
            'M=D'
        ]

        end: [str] = [  # goto functionName, set returnAddress label
            f'@{fName}',  # todo this will need a filename later
            '0;JMP',
            f'(retAddr_{self.retAddrCounter})'
        ]

        results.extend(header)
        results.extend(nArgsCheck)
        results.extend(saveFrame)
        results.extend(setArg)
        results.extend(setLcl)
        results.extend(end)

        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def writeReturn(self, command: str) -> [str]:
        """
        pseudocode
            endFrame = LCL
            *ARG = pop()
            SP = ARG+1
            THAT = *(endFrame-1)
            THIS = *(endFrame-2)
            ARG = *(endFrame-3)
            LCL = *(endFrame-4)
            retAddr = *(endFrame-5)
            goto retAddr
        :param command:
        :return:

        Recall that RAM[0-4] are: SP, LCL, ARG, THIS, THAT, so LCL is RAM[1]
        → LCL = *(endFrame-4)
            @endFrame
            D=M
            @4              # calculate endFrame-4 and put it into D
            D=D-A
            A=D             # select memory at address endFrame-4
            D=M
            @LCL            # store *(endFrame-4) → LCL
            M=D

        → cody suggests we decrement endFrame a few times and set it to memsegs
        → this method mutates endFrame by decrementing it each assignment
            we use this mutation to assign THAT, THIS, ARG, LCL
        → start with endFrame-1
                LCL = *(endFrame-4)
                ARG = *(endFrame-3)
                THIS = *(endFrame-2)
                THAT = *(endFrame-1)

        # → retAddr = *(endFrame-5)
            '@endFrame',    # calculate endFrame-5
            'D=M',
            '@5',
            'D=D-A',        # endFrame-5 → register D
            'A=D',          # select address in D
            'D=M',          # D = *(endFrame-5)
            '@retAddr',
            'M=D',          # set retAddr variable to *(endFrame-5)
        """
        results = [
            '// [ VM COMMAND ] ' + command,

            # → endFrame = LCL
            '@LCL',         # this is @1
            'D=M',          # M is the value of RAM[1], address where LCL begins
            '@endFrame',    # initialize endFrame variable, used by assembler
            'M=D',          # now endFrame's value is location LCL points to

            # → *ARG = pop()    # puts return value into segment argument 0
            '@SP',
            'AM=M-1',       # select RAM[SP-1], decrement SP
            'D=M',          # RAM[SP-1] → register D
            '@ARG',         # find ARG; it's @2!
            'A=M',
            'M=D',          # stuff RAM[SP-1] into RAM[ARG]

            # → SP = ARG+1  # set the stack pointer to just ahead of caller's
                            # working stack
            '@ARG',         # this is where ARG resides in RAM
            'D=M+1',
            '@SP',          # set SP to ARG+1
            'M=D',

            # endFrame minus 1-4 memory segment restoration
            '@endFrame',
            'AM=M-1',       # select address: endFrame-1. note endFrame has
                            # been permanently decremented because M=M-1
            'D=M',          # *(endFrame-1) → D
            '@THAT',
            'M=D',          # set *(endFrame-1) to THAT

            '@endFrame',    # set *(endFrame-2) to THIS
            'AM=M-1',
            'D=M',
            '@THIS',
            'M=D',

            '@endFrame',    # set *(endFrame-3) to ARG
            'AM=M-1',
            'D=M',
            '@ARG',
            'M=D',

            '@endFrame',    # set *(endFrame-4) to LCL
            'AM=M-1',
            'D=M',
            '@LCL',
            'M=D',

            # → goto retAddr, conveniently *(endFrame-5)
            '@endFrame',
            'AM=M-1',
            'A=M',
            '0;JMP'
        ]
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def writeFunction(self, command: str, fName: str, nVars: int) -> [str]:
        """
        always follows call
        → (functionName)
        → repeat 'push 0' nVars times, but always push one if nVars is 0

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
        :param command: a string like 'function factorial(nVars)'
        :param nVars: the nVars part of 'function factorial(nVars)'
        :param fName: the factorial part of 'function factorial(nVars)'
        :return: a list of assembly commands
        """

        loopCode: [str] = [  # executes 'push 0' once
            '@SP',
            'A=M',  # select as memory location: value at SP
            'M=0',  # set top of stack to 0
            '@SP',  # increment SP
            'M=M+1'
        ]

        nVars = int(nVars)
        if nVars < 0:
            raise ValueError(f'nVars < 0 in: {command}')

        loops: int = nVars  # how many times are we executing 'push 0'?
        results: [str] = [
            '// [ VM COMMAND ] ' + command,
            f'({fName})'
        ]

        for index in range(loops):
            results.extend(loopCode)

        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def writeLabel(self, command: str, label: str) -> [str]:
        results = [  # hackAssembler handles labels on its 1st pass
            '// [ VM COMMAND ] ' + command,
            f'({label})'
        ]
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def writeGotoLabel(self, command: str, label: str) -> [str]:
        results = [
            '// [ VM COMMAND ] ' + command,
            f'@{label}',
            '0;JMP'         # unconditional jump to specified label
        ]
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def writeIfGotoLabel(self, command: str, label: str) -> [str]:
        results = [  # hackAssembler handles labels on its 1st pass
            '// [ VM COMMAND ] ' + command,
            '@SP',
            'AM=M-1',       # select *[SP-1]
            'D=M',
            f'@{label}',   # TODO add function name once we have multiple files
            'D;JNE'        # we just if *[SP-1] is true; note 0 is false
        ]
        self.__writelines(results)

    # writes to output file the asm commands that implement the vm command given
    def writeArithmetic(self, command) -> [str]:  # List[str] requires import
        # remember to add comments to each command!
        # arith = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

        # print(f'{command}→{command.split()[0]}')
        result = []
        match command.split()[0]:
            case 'neg':
                self.__writeNeg()
            case 'add':
                self.__writeAdd()
            case 'sub':
                self.__writeSub()
            case 'eq':
                self.__writeEq()
            case 'lt':
                self.__writeLt()
            case 'gt':
                self.__writeGt()
            case 'not':
                self.__writeNot()
            case 'and':
                self.__writeAnd()
            case 'or':
                self.__writeOr()
            case _:
                print(f'command not found: {command}')

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
                    self.__writePopTemp(command, n)
                elif segment == 'pointer':
                    self.__writePopPointer(command, n)
                elif segment == 'static':
                    self.__writePopStatic(command, n)
                else:
                    self.__writePopLATT(command, segDict[segment], n)
            case 'push':
                # take care of push constant i
                if segment == 'constant':
                    self.__writePushConstant(command, n)
                elif segment == 'temp':
                    self.__writePushTemp(command, n)
                elif segment == 'pointer':
                    self.__writePushPointer(command, n)
                elif segment == 'static':
                    self.__writePushStatic(command, n)
                else:
                    self.__writePushLATT(command, segDict[segment], n)
            case _:
                raise ValueError(f'{command} is not valid in writePushPop')

    # noinspection PyMethodMayBeStatic
    def __writeEq(self) -> [str]:
        self.__writelines(self.__equalityHelper('EQ'))

    # noinspection PyMethodMayBeStatic
    def __writeLt(self) -> [str]:
        self.__writelines(self.__equalityHelper('LT'))

    # noinspection PyMethodMayBeStatic
    def __writeGt(self) -> [str]:
        self.__writelines(self.__equalityHelper('GT'))

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

        # below, when SP-1 or SP-2 are mentioned, they refer to the top and 2nd
        # values of the stack, where SP-1 is the top
        results = [
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
        results = [        # when SP is mentioned, it refers to the original SP
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
        self.__writelines(results)

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
        results = [        # when SP is mentioned, it refers to the original SP
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writeAdd(self) -> [str]:
        results = [
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writeSub(self) -> [str]:
        # we always want the deeper stack element to subtract the shallower one
        #   push 5, push 1, sub → 5-1=4
        results = [
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writeNeg(self) -> [str]:
        results = [
            '// [ VM COMMAND ] neg',
            '@SP',
            'A=M-1',
            'M=-M'
        ]
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writeNot(self) -> [str]:
        results = [
            '// [ VM COMMAND ] not',
            '@SP',
            'A=M-1',    # shortened from M=M-1; A=M
            'M=!M'      # don't need @SP; M=M+1
        ]
        self.__writelines(results)

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
        results = [
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
        self.__writelines(results)

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
        results = [
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writePushStatic(self, command: str, n: int) -> [str]:
        results = [
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writePopStatic(self, command: str, n: int) -> [str]:
        results = [
            # pop static 5 means store *[SP-1] into new variable @Foo.5
            '// [ VM COMMAND ] ' + command,
            '@SP',
            'AM=M-1',
            'D=M',      # D ← top element of stack

            f'@Kiwi.{str(n)}',
            'M=D'
        ]
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writePushPointer(self, command: str, n: int) -> [str]:
        results = [
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writePopPointer(self, command: str, n: int) -> [str]:
        results = [
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writePushConstant(self, command: str, n: int) -> [str]:
        results = [
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writePopTemp(self, command: str, n: int):
        results = [
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
        self.__writelines(results)

    # noinspection PyMethodMayBeStatic
    def __writePushTemp(self, command: str, n: int):
        results = [
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
        self.__writelines(results)

    def __writelines(self, lines: [str]):
        # adds newlines between every entry in lines
        self.output.write('\n'.join(lines) + '\n')

    def close(self):
        self.output.close()
