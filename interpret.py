import re
import sys
from sys import stderr
import argparse
import xml.etree.ElementTree as ET

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
        