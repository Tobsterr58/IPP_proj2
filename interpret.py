import re
import sys
import argparse
import xml.etree.ElementTree as ET

# dictionary of number of arguments for each instruction
instructionNumOfArguments = {
    0 : ('CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK'),
    1 : ('DEFVAR', 'POPS', 'CALL', 'LABEL', 'JUMP', 'PUSHS', 'WRITE', 'EXIT', 'DPRINT'),
    2 : ('MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'READ', 'NOT'),
    3 : ('ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'JUMPIFEQ', 'JUMPIFNEQ', 'OR', 'AND', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR')
}

# dictionary of instructions and their argument types
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
    'STRLEN'      :  ['VAR', 'SYMB', None],
    'TYPE'        :  ['VAR', 'SYMB', None],   
    'NOT'         :  ['VAR', 'SYMB', None], # NOT is spesial case, because it has only 2 arguments
    'READ'        :  ['VAR', 'TYPE', None],
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

# function for swapping values in frames
def swapFrames(first :str, second: str):
    for variable in list(variableList.keys()):
            replacedVariable = variable.replace(first, second)
            variableList[replacedVariable] = variableList.pop(variable)

def checkArgumentCorrectness(child):
    args = []
    for subelem in child:
        if not re.match(r'^arg[1-3]$', subelem.tag):
            sys.stderr.write("Invalid argument tag: " + subelem.tag + "\n")
            sys.exit(32)
        args.append(subelem.tag)
    args = sorted(args)  
    arg_num = len(args)
    if arg_num == 1 and args[0] != 'arg1':
        sys.stderr.write("Invalid argument tag: " + args[0] + "\n")
        sys.exit(32)
    elif arg_num == 2 and args[0] != 'arg1' and args[1] != 'arg2':
        sys.stderr.write("Invalid argument tag: " + args[0] + "\n")
        sys.exit(32)
    elif arg_num == 3 and args[0] != 'arg1' and args[1] != 'arg2' and args[2] != 'arg3':
        sys.stderr.write("Invalid argument tag: " + args[0] + "\n")
        sys.exit(32)
                       
class Labels:
    def __init__(self, input_file):
        self.root = ET.parse(input_file).getroot()
        self.input_file = input_file
    
        self.findLabels()
    
    def findLabels(self):
        counter = 0 # counter of instructions where label is
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
    
    def checkArgumentsType(self, arg_type):
        if arg_type == self.arg_type or arg_type == 'VAR':
            pass
        elif arg_type == "SYMB" and self.arg_type in ('VAR', 'INT', 'STRING', 'BOOL', 'NIL'):
            pass
        elif arg_type == "TYPE" and self.arg_type in ('int', 'string', 'bool'):
            pass
        elif arg_type == "LABEL" and self.arg_type == 'LABEL':
            pass
        else:
            sys.stderr.write("Invalid argument type \n")
            if opcodes == "READ":
                sys.exit(32)
            else:
                sys.exit(53)
            
    def checkArguments(self):
        self.checkArgumentsType(instructionTypes[opcodes][self.num-1])
        if self.arg_type == 'VAR' and not opcodes == 'DEFVAR':
            if self.arg_value.startswith('LF') and LfCount == 0: 
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
        self.checkTypeConversion()
        self.replaceSequence()
        if self.arg_value is None and opcodes != 'TYPE':
            sys.stderr.write("Invalid argument value \n")
            sys.exit(53)            

    def checkTypeConversion(self):
        conversion_rules = {
            'INT': lambda x: int(x),
            'BOOL': lambda x: self.convert_bool(x),
            'NIL': lambda x: 'nil'
        }
        
        conversion_func = conversion_rules.get(self.arg_type)
        if conversion_func:
            try:
                self.arg_value = conversion_func(self.arg_value)
            except ValueError:
                #print("Som tu")
                sys.stderr.write("Invalid argument value \n")
                sys.exit(32)
        else:
            return

    def convert_bool(self, arg_value):
        if arg_value == 'true' or arg_value == True:
            return True
        elif arg_value == 'false' or arg_value == False:
            return False
        else:
            sys.stderr.write("Invalid argument value \n")
            sys.exit(53)

        
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
     
    # getters to get the argument type and value anytime for instruction in While loop          
    def getType(self):
        return self.arg_type
    
    def getValue(self):
        return self.arg_value
            
            
# define the Instruction class
class Instruction:
    def __init__(self, opcode, num, arguments):
        self.opcode = opcode
        self.num = num
        self.type: str

        self.checkOpcode()

        self.arg_types = instructionTypes[self.opcode]
        
        self.checkArg()
                
        self.arg1 = Argument(1, (arguments[0].get('type')).upper(), arguments[0].text) if num > 0 else None
        self.arg2 = Argument(2, (arguments[1].get('type')).upper(), arguments[1].text) if num > 1 else None
        self.arg3 = Argument(3, (arguments[2].get('type')).upper(), arguments[2].text) if num > 2 else None
    
        if self.arg1: self.arg1.checkArguments()
        if self.arg2: self.arg2.checkArguments()
        if self.arg3: self.arg3.checkArguments()

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
instNumToExecute = 0
LfCount = 0
TfCreated = False
TfExists = False
EOF = False
Stack = [] # normal stack for stack instructions
LfStack = [] # stack of local frames (that cant be used)
labels = {} # dictionary of labels
callList = [] # stack for CALL and RETURN instructions
orderList = [] # list of numbers in order

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
        inputs = open(args.input)
    else:
        inputs = sys.stdin
except OSError as e:
    sys.stderr.write("Something went wrong with trying to reach input file\n")
    sys.exit(11)
    
try:
    tree = ET.fromstring(source_code)
except ET.ParseError:
    sys.stderr.write("XML format is not right\n")
    sys.exit(31)

# XML load
tree = ET.fromstring(source_code)
root = tree

    # XML check and parse
if root.tag != "program":
    sys.stderr.write("Missing 'program' tag\n")
    sys.exit(32)
        
if not ("language" in root.attrib.keys() and root.attrib['language'] == "IPPcode23"):
    sys.stderr.write("Wrong language. Must be IPPcode23\n")
    sys.exit(32)
    
for child in root: 
    if child.tag != "instruction":
        sys.stderr.write("Missing 'instruction'\n")
        sys.exit(32)
    keysList = list(child.attrib.keys())
    if not ("order" in keysList and "opcode" in keysList):
        sys.stderr.write("Missing 'order' or 'opcode'\n")
        sys.exit(32)
    
    checkArgumentCorrectness(child)
    
    if not child.attrib['order'].isdigit():
        sys.stderr.write("Order number is not a number\n")
        sys.exit(32)
    if(orderList.count(int(child.attrib['order']))>0):
        sys.stderr.write("Order number is not unique\n")
        sys.exit(32)
    elif int(child.attrib['order']) < 1:
        sys.stderr.write("Order must be greater than 0\n")
        sys.exit(32)
    orderList.append(int(child.attrib['order']))
   
#After XML check, sort the instructions by order    
sortedByOrder [:] = sorted(root, key=lambda c: int(c.attrib['order']))
    
###########################################
######## EXECUTION OF INSTRUCTIONS ########
###########################################
    
Labels(args.source)
while True: 
    try:
        root = sortedByOrder[instNumToExecute]
    except:
        sys.exit(0)
    
    TfDict = {} # dictionary of temporary frames
    opcodes = root.get('opcode').upper() # get opcode
    numberOfArgs = len(sortedByOrder[instNumToExecute]) # get number of arguments
    arguments = []
    arguments[:] = sorted(root,key=lambda x: x.tag)
    instruction=Instruction(opcodes, numberOfArgs, arguments)
    
    #print(opcodes)    
        
    if instruction.arg1:
        valueArg1 = instruction.arg1.getValue()
        typeArg1 = instruction.arg1.getType()
    if instruction.arg2:
        valueArg2 = instruction.arg2.getValue()
        typeArg2 = instruction.arg2.getType()
    if instruction.arg3:
        valueArg3 = instruction.arg3.getValue()
        typeArg3 = instruction.arg3.getType()
          
    ################# INSTRUCTIONS #################
    
    ### Instructions with 0 arguments ###
    
    # CREATEFRAME
    if opcodes == "CREATEFRAME":
        if TfExists:
            [variableList.pop(key) for key in list(variableList.keys()) if key.startswith("TF")]
        TfCreated = True
        TfExists = True
        
    # PUSHFRAME
    elif opcodes == "PUSHFRAME":
        if not TfCreated:
            sys.stderr.write("[PUSHFRAME] No frame to push\n")
            sys.exit(55)
            
        LfCount += 1
        
        for variable in list(variableList.keys()):
            if variable.startswith("LF"):
                TfDict[variable] = variableList.pop(variable)
        LfStack.append(TfDict)
            
        swapFrames("TF", "LF")
            
        TfCreated = False
        TfExists = False
        
    # POPFRAME
    elif opcodes == "POPFRAME":
        if LfCount == 0:
            sys.stderr.write("[POPFRAME] No frame to pop\n")
            sys.exit(55)
        if TfExists == True:
            [variableList.pop(key) for key in list(variableList.keys()) if key.startswith("TF")]
        
        swapFrames("LF", "TF")
        
        variableList.update(LfStack.pop())
        LfCount -= 1
        TfCreated = True
        TfExists = True
        
    # RETURN 
    elif opcodes == "RETURN":
        if not callList:
            sys.stderr.write("[RETURN] No frame to return\n")
            sys.exit(56)
        else:
            instNumToExecute = callList.pop()
         
    
    # BREAK  
    elif opcodes == "BREAK":
        sys.stderr.write("BREAK - Current situation of interpreter\n")
        
### Instructions with 1 argument ###

    # DEFVAR
    elif opcodes == "DEFVAR":
        if valueArg1 in variableList:
            sys.stderr.write("[DEFVAR] Variable already exists\n")
            sys.exit(52)
        if valueArg1.startswith("TF") and TfExists:
            variableList[valueArg1] = [None, None]
        elif valueArg1.startswith("LF") and not LfCount == 0:
            variableList[valueArg1] = [None, None]
        elif valueArg1.startswith("GF"):
            variableList[valueArg1] = [None, None]
        else:
            sys.stderr.write("[DEFVAR] Wrong frame\n")
            sys.exit(55)
            
    # POPS
    elif opcodes == "POPS":
        if not Stack:
            sys.stderr.write("[POPS] No data to pop\n")
            sys.exit(56)
        else:
            popped = Stack.pop()
            variableList [valueArg1][0] = popped[0]
            variableList [valueArg1][1] = popped[1]
            
    # CALL
    elif opcodes == "CALL":
        if valueArg1 not in labels:
            sys.stderr.write("[CALL] Label does not exist\n")
            sys.exit(52)
        else:
            callList.append(instNumToExecute)
            instNumToExecute = labels[valueArg1]
            
    # LABEL
    # Already done in Labels function

    # JUMP
    elif opcodes == "JUMP":
        if not valueArg1 in labels:
            sys.stderr.write("[JUMP] Label does not exist\n")
            sys.exit(52)
        instNumToExecute = labels[valueArg1]

    # PUSHS
    elif opcodes == "PUSHS" :
        if typeArg1 == "VAR":
            valueArg1 = variableList[valueArg1][0]
            if valueArg1 == None:
                sys.stderr.write("[PUSHS] Argument value can not be undefined\n")
                sys.exit(56)
            Stack.append([valueArg1, typeArg1])
        else:
            Stack.append([valueArg1, typeArg1]) 
            
    # WRITE
    elif opcodes == "WRITE":
        value = str(valueArg1)
        type = str(typeArg1)
        if typeArg1 == "VAR":
            if variableList[valueArg1][0] == None:
                sys.stderr.write("[WRITE] Argument value can not be undefined\n")
                sys.exit(56)
            value = str(variableList[valueArg1][0])
            type = str(variableList[valueArg1][1])
        if value == "False":
            value = 'false'
        elif value == "True":
            value = 'true'
        elif value == "nil":
            if type == "STRING":
                value = 'nil'
            else:
                value = ''
        print(value, end="")
        
    # EXIT
    elif opcodes == "EXIT":
        if typeArg1 == "VAR":
            typeArg1 = variableList[valueArg1][1]
            valueArg1 = variableList[valueArg1][0]
        if valueArg1 == None:
            sys.stderr.write("[EXIT] Argument value can not be undefined\n")
            sys.exit(56)
        if typeArg1 != "INT":
            sys.stderr.write("[EXIT] Wrong type of argument\n")
            sys.exit(53)
        if int(valueArg1) < 0 or int(valueArg1) > 49:
            sys.stderr.write("[EXIT] Wrong value of argument\n")
            sys.exit(57)
        exit(valueArg1)
        
    # DPRINT
    elif opcodes == "DPRINT":
        if typeArg1 == "VAR":
            typeArg1 = variableList[valueArg1][1]
            valueArg1 = variableList[valueArg1][0]
        if valueArg1 == None:
            sys.stderr.write("Argument can not be undefined\n")
            sys.exit(56)
        print(valueArg1, file=sys.stderr)
    
### Instructions with 2 arguments ###

    # MOVE
    elif opcodes == "MOVE":
            variableList[valueArg1][0] = valueArg2
            variableList[valueArg1][1] = typeArg2
        
    # INT2CHAR
    elif opcodes == "INT2CHAR":
        if typeArg2 != "INT":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        if not 0 < valueArg2 < 256:
            sys.stderr.write("Wrong value of argument\n")
            sys.exit(58)
        variableList[valueArg1][0] = chr(valueArg2)
        variableList[valueArg1][1] = 'STRING'
        
            
    # STRLEN
    elif opcodes == "STRLEN":
        if typeArg2 != "STRING":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        variableList[valueArg1][0] = len(valueArg2)
        variableList[valueArg1][1] = 'INT'
        
    # TYPE
    elif opcodes == "TYPE":
        if typeArg2 in ["INT", "STRING", "BOOL", "NIL"]:
            variableList[valueArg1][0] = typeArg2.lower()
            variableList[valueArg1][1] = 'STRING'
        else:
            variableList[valueArg1][0] = ''
            variableList[valueArg1][1] = 'STRING'
    
    # AND, OR, NOT
    elif opcodes in ["AND", "OR", "NOT"]:
        if typeArg2 != "BOOL":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        if opcodes == "NOT":
            if valueArg2 == True:
                variableList[valueArg1][0] = False
            elif valueArg2 == False:
                variableList[valueArg1][0] = True
        else:
            if typeArg3 != "BOOL":
                sys.stderr.write("Wrong type of argument\n")
                sys.exit(53)
            if opcodes == "AND":
                if valueArg2 == True and valueArg3 == True:
                    variableList[valueArg1][0] = True
                elif valueArg2 == False and valueArg3 == False:
                    variableList[valueArg1][0] = False
                elif valueArg2 == True and valueArg3 == False:
                    variableList[valueArg1][0] = False
                elif valueArg2 == False and valueArg3 == True:
                    variableList[valueArg1][0] = False
            elif opcodes == "OR":
                if valueArg2 == True and valueArg3 == True:
                    variableList[valueArg1][0] = True
                elif valueArg2 == False and valueArg3 == False:
                    variableList[valueArg1][0] = False
                elif valueArg2 == True and valueArg3 == False:
                    variableList[valueArg1][0] = True
                elif valueArg2 == False and valueArg3 == True:
                    variableList[valueArg1][0] = True
        variableList[valueArg1][1] = 'BOOL'
        
    # READ
    elif opcodes == "READ":
        typeArg2 = (arguments[1].text).upper()
        inputValue = inputs.readline()
        if not inputValue: EOF = True
        if EOF == False and inputValue[-1] == '\n':
            inputValue = inputValue[:-1]
        if typeArg2 == "INT":
            try:
                variableList[valueArg1][0] = int(inputValue)
                variableList[valueArg1][1] = 'INT'
            except:
                variableList[valueArg1][0] = 'nil'
                variableList[valueArg1][1] = 'NIL'
        elif typeArg2 == "STRING" and not EOF:
            variableList[valueArg1][0] = inputValue
            variableList[valueArg1][1] = 'STRING'
        elif typeArg2 == "BOOL":
            if inputValue.lower() == 'true':
                variableList[valueArg1][0] = True
                variableList[valueArg1][1] = 'BOOL'
            else :
                variableList[valueArg1][0] = False
                variableList[valueArg1][1] = 'BOOL'
        else:
            variableList[valueArg1][0] = 'nil'
            variableList[valueArg1][1] = 'NIL' 
    
    # ADD, SUB, MUL, IDIV
    elif opcodes in ["ADD", "SUB", "MUL", "IDIV"]:
        if typeArg2 != "INT" or typeArg3 != "INT":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        if opcodes == "ADD":
            variableList[valueArg1][0] = valueArg2 + valueArg3
        elif opcodes == "SUB":
            variableList[valueArg1][0] = valueArg2 - valueArg3
        elif opcodes == "MUL":
            variableList[valueArg1][0] = valueArg2 * valueArg3
        elif opcodes == "IDIV":
            if valueArg3 == 0:
                sys.stderr.write("Division by zero\n")
                sys.exit(57)
            variableList[valueArg1][0] = valueArg2 // valueArg3
        variableList[valueArg1][1] = 'INT'
        
    # LT, GT, EQ
    elif opcodes in ["LT", "GT", "EQ"]:
        if opcodes == "LT":
            if typeArg2 == "NIL" or typeArg3 == "NIL":
                sys.stderr.write("Wrong type of argument\n")
                sys.exit(53)
            if typeArg2 != typeArg3:
                sys.stderr.write("Wrong type of argument\n")
                sys.exit(53)
            if valueArg2 < valueArg3:
                variableList[valueArg1][0] = True
            else:
                variableList[valueArg1][0] = False
        elif opcodes == "GT":
            if typeArg2 == "NIL" or typeArg3 == "NIL":
                sys.stderr.write("Wrong type of argument\n")
                sys.exit(53)
            if typeArg2 != typeArg3:
                sys.stderr.write("Wrong type of argument\n")
                sys.exit(53)
            if valueArg2 > valueArg3:
                variableList[valueArg1][0] = True
            else:
                variableList[valueArg1][0] = False
        elif opcodes == "EQ":
            if typeArg2 != typeArg3:
                if typeArg2 == "NIL" or typeArg3 == "NIL":
                    pass
                else:
                    sys.stderr.write("Wrong type of argument\n")
                    sys.exit(53)
            if valueArg2 == valueArg3:
                variableList[valueArg1][0] = True
            else:
                variableList[valueArg1][0] = False
        variableList[valueArg1][1] = 'BOOL'
        
    # JUMPIFEQ JUMPIFNEQ
    elif opcodes in ["JUMPIFEQ", "JUMPIFNEQ"]:
        if not valueArg1 in labels:
            sys.stderr.write("Wrong label\n")
            sys.exit(52)
        if typeArg2 != typeArg3:
            if typeArg2 == "NIL" or typeArg3 == "NIL":
                pass
            else:
                sys.stderr.write("Wrong type of argument\n")
                sys.exit(53)
        if opcodes == "JUMPIFEQ" and valueArg2 == valueArg3:
            instNumToExecute = labels[valueArg1]
        if opcodes == "JUMPIFNEQ" and valueArg2 != valueArg3:
            instNumToExecute = labels[valueArg1]
            
    # STRI2INT
    elif opcodes == "STRI2INT":
        if typeArg2 != "STRING" or typeArg3 != "INT":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        if valueArg3 < 0 or valueArg3 >= len(valueArg2):
            sys.stderr.write("Wrong index\n")
            sys.exit(58)
        variableList[valueArg1][0] = ord(valueArg2[valueArg3])
        variableList[valueArg1][1] = 'INT'
        
    # CONCAT
    elif opcodes == "CONCAT":
        if typeArg2 != "STRING" or typeArg3 != "STRING":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        variableList[valueArg1][0] = valueArg2 + valueArg3
        variableList[valueArg1][1] = 'STRING'
        
    # GETCHAR
    elif opcodes == "GETCHAR":
        if typeArg2 != "STRING" or typeArg3 != "INT":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        if valueArg3 > len(valueArg2)-1 or valueArg3 < 0:
            sys.stderr.write("Wrong index\n")
            sys.exit(58)
        variableList[valueArg1][0] = valueArg2[valueArg3]
        variableList[valueArg1][1] = 'STRING'
        
    # SETCHAR
    elif opcodes == "SETCHAR":
        if variableList[valueArg1][1] != "STRING":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        if variableList[valueArg1][0] == None:
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(56)
        if typeArg2 != "INT" or typeArg3 != "STRING":
            sys.stderr.write("Wrong type of argument\n")
            sys.exit(53)
        string = variableList[valueArg1][0]
        index = valueArg3
        if len(index) == 0:
            sys.stderr.write("Wrong index\n")
            sys.exit(58)
        lenArg1 = len(string) - 1
        if valueArg2 < 0 or valueArg2 > lenArg1:
            sys.stderr.write("Wrong index\n")
            sys.exit(58)
        variableList[valueArg1][0] = string[:valueArg2] + valueArg3[0] + string[valueArg2+1:]
        
    instNumToExecute += 1   
    

        