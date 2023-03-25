import re
import sys
import argparse
import xml.etree.ElementTree as ET


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
if args.source:
    with open(args.source) as f:
        source_code = f.read()
else:
    source_code = sys.stdin.read()

# Read inputs from input file or standard input
if args.input:
    with open(args.input) as f:
        inputs = f.read().splitlines()
else:
    inputs = sys.stdin.read().splitlines()