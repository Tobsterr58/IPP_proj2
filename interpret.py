import re
import sys
from sys import stderr
import argparse
import xml.etree.ElementTree as ET

# dictionary of number of arguments for each instruction
instructionNumOfArguments = {
    0 : ('CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK'),
    1 : ('DEFVAR', 'POPS', 'CALL', 'LABEL', 'JUMP', 'PUSHS', 'WRITE', 'EXIT', 'DPRINT'),
    2 : ('MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'READ',  'NOT'),
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

class arg:
    def __init__(self, arg_type, arg_value):
        self.arg_type = arg_type
        self.arg_value = arg_value

class instruction:
    def __init__(self, order, opcode):
        self.order = order
        self.opcode = opcode
    def add_arg(self, arg_type, arg_value):
        self.args.append(arg(arg_type, arg_value))
        

#TODO najst help xd
parser = argparse.ArgumentParser()
parser.add_argument("--source", metavar="file", help="input file with XML representation of source code")
parser.add_argument("--input", metavar="file", help="input file with inputs for program")
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
    sys.exit(11)

# Read inputs from input file or standard input
try:
    if args.input:
        with open(args.input) as f:
            inputs = f.read().splitlines()
    else:
        inputs = sys.stdin.read().splitlines()
except OSError as e:
    sys.exit(11)
    
try:
    tree = ET.fromstring(source_code)
except ET.ParseError:
    sys.exit(31)
    
# XML load
root = tree

# XML check and parse
if root.tag != "program":
    sys.exit(31)

for child in root:
    if child.tag != "instruction":
        sys.exit(31)
    keysList = list(child.attrib.keys())
    if not ("order" in keysList and "opcode" in keysList):
        sys.exit(31)
    for subelem in child:
        if not (re.match(r'^arg[1-3]+$', subelem.tag)):
            sys.exit(31)
        else:
            print(subelem.tag)

# everything is correct
sys.exit(0)
        