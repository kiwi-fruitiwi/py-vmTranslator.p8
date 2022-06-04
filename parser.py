import enum


class Command(enum.Enum):  # TODO remove the C_ prefix :p
    ARITHMETIC = 1
    PUSH = 2
    POP = 3
    LABEL = 4
    GOTO = 5
    IF = 6
    FUNCTION = 7
    RETURN = 8
    CALL = 9
    IF_GOTO = 10


class Parser:
    """
    handles the parsing of a single .vm file; reads a vm command, parses the
    command into its lexical components, and provides convenient access to
    said components. ignores all whitespace and comments
    """

    def __init__(self, filename):
        """
        opens a .vm file and saves all vm commands for later processing but
        does not include comments or whitespace
        :param filename:
        """

        vm_file = open(filename, 'r')
        lines = vm_file.readlines()
        self.vm_commands = []
        self.commandIndex = -1  # current command index;
        self.currentCommand = None  # initially there is no current command

        for line in lines:
            # ignore whitespace
            if line == '\n':
                continue

            # ignore entire-line comments
            if line[0] == '/' and line[1] == '/':
                continue

            # ignore mid-line comments
            try:
                index = line.index('//')
                line = line[0:index]
            except ValueError:
                # '//' wasn't found!
                pass

            # strip whitespace
            line = line.strip()

            self.vm_commands.append(line)


    def command(self) -> str:
        """
        returns the current VM command
        """
        return self.currentCommand


    def hasMoreCommands(self) -> bool:
        """
        :return: true if the parser contains more commands to be parsed
        """
        return self.commandIndex < len(self.vm_commands) - 1


    def advance(self) -> None:
        """
        goes to the next vm command if there are any
        """
        self.commandIndex += 1
        self.currentCommand = self.vm_commands[self.commandIndex]


    def commandType(self) -> Command:
        """
        :return: a Command enumeration corresponding to the command type of
        the current vm command
        """

        current = self.command()
        tokens = current.split()

        command_name = tokens[0]  # command's name is always the first token
        arithmetic = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

        if command_name in arithmetic:
            return Command.ARITHMETIC

        if command_name == 'pop':
            return Command.POP

        if command_name == 'push':
            return Command.PUSH

        if command_name == 'label':
            return Command.LABEL

        if command_name == 'if-goto':
            return Command.IF_GOTO

        if command_name == 'goto':
            return Command.GOTO

        raise ValueError(f'VM command not recognized: {self.command()}')


    def arg1(self) -> str:
        # TODO check: don't call if c_return
        return self.command().split()[1]


    def arg2(self) -> str:
        # TODO check: call only if current command is push, pop, function, call
        return self.command().split()[2]
