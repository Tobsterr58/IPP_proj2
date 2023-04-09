import re
import sys
from sys import stderr
import argparse
import xml.etree.ElementTree as ET

# dictionary of number of arguments for each instruction
instructionNumOfArguments = {
    0 : ('CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK'),
    1 : ('DEFVAR', 'POPS', 'CALL', 'LABEL', 'JUMP', 'PUSHS', 'WRITE', 'EXIT', 'DPRINT',  'NOT'),
    2 : ('MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'READ'),
    3 : ('ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'JUMPIFEQ', 'JUMPIFNEQ', 'OR', 'AND', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR')
}

# dictionary of instructions and their arguments
instructionTypes = {
    'CREATEFRAME' :  [None, None, None],
    'PUSHFRAME'   :  [None, None, None],
    'POPFRAME'    :  [None, None, None],
    'RETURN'      :  [None, None, None],
    'BREAK'       :  [None, None, None],
    'DEFVAR'      :  ['VAR', None, None],
    'POPS'        :  ['VAR', None, None],
    'CALL'        :  ['LABEL', None, None],
    'LABEL'       :  ['LABEL', None, None],
    'JUMP'        :  ['LABEL', None, None],
    'PUSHS'       :  ['SYMB', None, None],
    'WRITE'       :  ['SYMB', None, None],
    'EXIT'        :  ['SYMB', None, None],
    'DPRINT'      :  ['SYMB', None, None],
    'MOVE'        :  ['VAR', 'SYMB', None],
    'INT2CHAR'    :  ['VAR', 'SYMB', None],
    'READ'        :  ['VAR', 'TYPE', None],
    'STRLEN'      :  ['VAR', 'SYMB', None],
    'TYPE'        :  ['VAR', 'SYMB', None],   
    'NOT'         :  ['VAR', 'SYMB', None], # NOT is spesial case, because it has only 2 arguments
    'ADD'         :  ['VAR', 'SYMB', 'SYMB'],
    'SUB'         :  ['VAR', 'SYMB', 'SYMB'],
    'MUL'         :  ['VAR', 'SYMB', 'SYMB'],
    'IDIV'        :  ['VAR', 'SYMB', 'SYMB'],
    'LT'          :  ['VAR', 'SYMB', 'SYMB'],
    'GT'          :  ['VAR', 'SYMB', 'SYMB'],
    'EQ'          :  ['VAR', 'SYMB', 'SYMB'],
    'JUMPIFEQ'    :  ['VAR', 'SYMB', 'SYMB'],
    'JUMPIFNEQ'   :  ['VAR', 'SYMB', 'SYMB'],
    'OR'          :  ['VAR', 'SYMB', 'SYMB'],
    'AND'         :  ['VAR', 'SYMB', 'SYMB'],
    'STRI2INT'    :  ['VAR', 'SYMB', 'SYMB'],
    'CONCAT'      :  ['VAR', 'SYMB', 'SYMB'],
    'GETCHAR'     :  ['VAR', 'SYMB', 'SYMB'],
    'SETCHAR'     :  ['VAR', 'SYMB', 'SYMB'],
}

        
class Execute:
    def __init__(self, input_file):
        self.root = ET.parse(input_file).getroot()
        self.input_file = input_file
    
        self.findLabels()
    
    def findLabels(self):
        counter = 1 # counter of instructions where label is
        for ins in self.root:
            if ins.get('opcode') == 'LABEL':
                if ins[0].text in labels:
                    sys.stderr.write("Label already exists \n")
                    sys.exit(52)
                labels[ins[0].text] = counter
            counter += 1

class Argument:
    def __init__(self, num, arg_type: str, arg_value):
        self.num = num
        self.arg_type = arg_type
        self.arg_value = arg_value
    
    def checkArgumentsType(self, typ):
        if typ == self.arg_type or typ == 'VAR':
            pass
        elif typ == "SYMB" and self.arg_type in ('VAR', 'INT', 'STRING', 'BOOL', 'NIL'):
            pass
        elif typ == "TYPE" and self.arg_type in ("int", "string", "bool"):
            pass
        elif typ == 'LABEL' and self.arg_type == 'LABEL':
            pass
        else:
            sys.stderr.write("Invalid argument type \n")
            sys.exit(53)
            
    def checkArguments(self):
        self.checkArgumentsType(instructionTypes[opcodes][self.num-1])
        if self.arg_type == 'VAR' and not opcodes == 'DEFVAR':
            if self.arg_value.startswith('LF') and not LfCount == 0: 
                sys.stderr.write("LF does not exist \n")
                sys.exit(55)
            if self.arg_value.startswith('TF') and not TfExists: 
                sys.stderr.write("TF does not exist \n")
                sys.exit(55)
            if not self.arg_value in variableList:
                sys.stderr.write("Variable does not exist \n")
                sys.exit(54)
            self.varName = self.arg_value
            if not self.num == 1:
                var = variableList[self.arg_value]
                self.arg_type = var[1]
                self.arg_value = var[0]               
        self.checkTypeConversion() # TODO
        self.replaceSequence() # TODO
        if self.arg_value is None and opcodes != 'TYPE':
            sys.stderr.write("Invalid argument value \n")
            sys.exit(56)            

    def checkTypeConversion(self):
        conversion_rules = {
            'INT': lambda x: int(x),
            'BOOL': lambda x: self.convert_bool(x),
            'NIL': lambda x: None
        }
        
        conversion_func = conversion_rules.get(self.arg_type)
        if conversion_func:
            try:
                self.arg_value = conversion_func(self.arg_value)
            except ValueError:
                sys.stderr.write("Invalid argument value \n")
                sys.exit(32)
        else:
            return

    def convert_bool(self, arg_value):
        if arg_value == 'true':
            return True
        elif arg_value == 'false':
            return False
        else:
            sys.stderr.write("Invalid argument value \n")
            sys.exit(32)

        
    def replaceSequence(self):
        if self.arg_type == 'STRING' and self.arg_value is None:
            self.arg_value = ''
        elif self.arg_type == 'STRING' and self.arg_value != '':
            tmp = re.findall(r'\\[0-9]{3}', self.arg_value)
            tmp = [string[1:] for string in tmp]
            tmp = list(map(int, tmp))
            for sequence in tmp:
                to_replace = '\\0' + str(sequence)
                self.arg_value = self.arg_value.replace(to_replace, chr(sequence))
            
            
# define the Instruction class
class Instruction:
    def __init__(self, opcode, num, arguments):
        self.opcode = opcode
        self.num = num
        self.arguments = arguments
        self.type: str

        self.checkOpcode()

        self.arg_types = instructionTypes[self.opcode]
        
        self.checkArg()
                
        self.arg1 = Argument(self.arg_types[0], None) if num > 0 else None
        self.arg2 = Argument(self.arg_types[1], None) if num > 1 else None
        self.arg3 = Argument(self.arg_types[2], None) if num > 2 else None
    
        if self.arg1: self.arg1.checkArgumentsType(self.arg1.arg_type)
        if self.arg2: self.arg2.checkArgumentsType(self.arg2.arg_type)
        if self.arg3: self.arg3.checkArgumentsType(self.arg3.arg_type)

    def checkOpcode(self):
        if not self.opcode in instructionTypes:
           sys.stderr.write("Invalid opcode \n")
           sys.exit(32)
           
    def checkArg(self):
        if not self.opcode in instructionNumOfArguments[self.num]:
            sys.stderr.write("Invalid number of arguments \n")
            sys.exit(32)
    
    def getOpcode(self):
        return self.opcode
    
    

########################### START OF THE INTERPRETER #########################

# important variables
whileCount = 0
LfCount = 0
TfCreated = False
TfExists = False
EOF = False
Stack = []
LfStack = [] 
labels = {} # dictionary of labels
sortedByOrder = [] # list of instructions sorted by order 
variableList = {} # dictionary of variables
            
# main function (som ani nevedel, ze to je treba xd)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", "-s", metavar="file")
    parser.add_argument("--input", "-i", metavar="file")
    args = parser.parse_args()

# If there is no argument, show help
if not any(vars(args).values()):
    parser.print_help(sys.stderr)
    sys.exit(10)

# Read source code from input file or standard input
try:
    if args.source:
        with open(args.source) as f:
            source_code = f.read()
    else:
        source_code = sys.stdin.read()
except OSError as e:
    sys.stderr.write("Something went wrong with trying to reach input file\n")
    sys.exit(11)

# Read inputs from input file or standard input
try:
    if args.input:
        with open(args.input) as f:
            inputs = f.read().splitlines()
    else:
        inputs = sys.stdin.read().splitlines()
except OSError as e:
    sys.stderr.write("Something went wrong with trying to reach input file\n")
    sys.exit(11)
    
try:
    tree = ET.fromstring(source_code)
except ET.ParseError:
    sys.stderr.write("Program does not start with 'program' header \n")
    sys.exit(31)
    
# XML load
tree = ET.fromstring(source_code)

# XML load
root = tree

    # XML check and parse
if root.tag != "program":
    sys.stderr.write("Missing 'program' tag\n")
    sys.exit(31)
        
if not ("language" in root.attrib.keys() and root.attrib['language'] == "IPPcode23"):
    sys.stderr.write("Wrong language. Must be IPPcode23\n")
    sys.exit(32)

order = 1 # maybe move it up
sortedByOrder [:] = sorted(root, key=lambda c: int(c.attrib['order']))
for ins in sortedByOrder: #in sorted(root, key=lambda c: int(c.attrib['order'])):
    if ins.tag != "instruction":
        sys.stderr.write("Missing 'instruction'\n")
        sys.exit(31)
    keysList = list(ins.attrib.keys())
    if not ("order" in keysList and "opcode" in keysList):
        sys.stderr.write("Missing 'order' or 'opcode'\n")
        sys.exit(31)
    if int(ins.attrib['order']) != order:
        sys.stderr.write("Wrong order number\n")
        sys.exit(32)
    for subelem in ins:
        if not (re.match(r'^arg[1-3]+$', subelem.tag)):
            sys.stderr.write("Wrong number in argument\n")
            sys.exit(31)

    order += 1
    
###########################################
######## EXECUTION OF INSTRUCTIONS ########
###########################################
    
program = Execute(args.source)

while True: 
    try:
        root = sortedByOrder[whileCount]
    except:
        sys.exit(0)

    TfDict = {} # dictionary of temporary frames
    opcodes = root.get('opcode').upper() # get opcode
    numberOfArgs = len(sortedByOrder[whileCount]) # get number of arguments
    arguments = []
    arguments[:] = sorted(root,key=lambda x: x.tag)
    instruction=Instruction(opcodes, numberOfArgs, arguments)
    print(instruction.arg_types)
    
    sys.exit(0)
    

        