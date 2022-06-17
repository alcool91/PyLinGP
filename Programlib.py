import math
import random
import copy
import statistics

NUM_WREG    = 24
NUM_CREG    = 6
MAX_LENGTH  = 12
MIN_LENGTH  = 1
FIT_CASES   = 50
DX          = (2 * math.pi) / FIT_CASES
CASES       = [0 + i*DX for i in range(FIT_CASES)]

def set_num_wreg(n):
    NUM_WREG = n
    
def set_num_creg(n):
    NUM_CREG = n

class Program:
    
    def __init__(self, reg_init='r', IS=['Add', 'Sub', 'Mul', 'Div', 'Sin', 'Mean', 'Copy', 'Sqrt', 'Sqr', 'Max', 'Min', 'Exp', 'Log', 'Lt', 'Gte', 'Eq', 'Neq', 'And', 'Or', 'Not', 'If'], inputs=1):
        """
        reg_init -> {
            'r': random,
            'z': zeros
        }
        how to initiate the registers
        """
        if reg_init == 'r':
            self.WREG = [random.random() for i in range(NUM_WREG)]  #writable registers
        elif reg_init == 'z':
            self.WREG = [0.0 for i in range(NUM_WREG)]              #writable registers
        self.reg_init = reg_init
        self.CREG = [-1.0] + [1/i for i in range(1,NUM_CREG)]        #Read-only (constant) registers
        self.IREG = [0.0] *inputs 
        self.REG  = self.WREG + self.CREG + self.IREG
        self.INST = []
        self.EFF_UPDATED = False
        self.PC   = 0
        self.IS   = IS
        self.inputs = inputs
        prg_len   = random.randint(MIN_LENGTH, MAX_LENGTH)
        for i in range(prg_len):
            self.INST.append(Instruction(len(self.WREG), len(self.CREG), num_ireg = self.inputs, instruction_set=self.IS))
            
    def num_wreg(self):
        return len(self.WREG)
    
    def num_creg(self):
        return len(self.CREG)
    
    def num_inp(self):
        return len(self.IREG)
    
    def num_reg(self):
        return len(self.REG)
    
    def load_from_file(self, filename):
        read_in_inst = []
        with open(filename, 'r+') as f:
            for line in f:
                data = line.split()
                inst = Instruction(len(self.WREG), len(self.CREG), instruction_set=self.IS, _random=False, name = data[0], op1 = int(data[1]), op2 = int(data[2]), dest = int(data[3]))
                read_in_inst.append(inst)
        self.INST = read_in_inst
        
    def _clone(self):
        return copy.deepcopy(self  )
    
    def _add_instruction(self, instruction_name):
        if instruction_name in self.IS:
            return
        else:
            self.IS.append(instruction_name)
            
    def _full_reset(self):
        """ Reset the instructions and registers 
            Useful if you change the instruction set"""
        self.reset()
        prg_len   = random.randint(MIN_LENGTH, MAX_LENGTH)
        for i in range(prg_len):
            self.INST.append(Instruction(len(self.WREG), len(self.CREG), num_ireg = self.inputs, instruction_set=self.IS))
        
    def _set_INST(self, prog):
        self.INST = prog
        
    def _remove_instruction(self, instruction_name):
        if instruction_name in self.IS:
            self.IS.remove(instruction_name)
        else:
            print(instruction_name, " not in instruction set.")
        
    def _set_input(self, _input):
        self._input  = _input
        self.REG[-1] = self._input
        
    def _set_inputs(self, _input):
        self._input  = _input
        self.input   = len(_input)
        self.IREG = list(self._input)
        self.REG  = self.WREG + self.CREG + self.IREG
            
            
    def reset(self, new_gen=False):
        if self.reg_init == 'r':
            self.WREG = [random.random() for i in range(NUM_WREG)]  #writable registers
        elif self.reg_init == 'z':
            self.WREG = [0.0 for i in range(NUM_WREG)]  #writable registers
        self.CREG = [-1.0] + [1/i for i in range(1,NUM_CREG)]        #Read-only (constant) registers
        self.IREG = [0.0]*self.inputs
        self.REG  = self.WREG + self.CREG + self.IREG
        self.PC   = 0
        if new_gen:
            self.EFF_UPDATED = False
            
    def __repr__(self):
        r = ""
        r += str(self.REG) + '\n'
        for i in range(len(self.INST)):
            r += str(self.INST[i]) + '\n'
        return(r)
    
    def print_effective_program(self):
        r = ""
        r += str(self.REG) + '\n'
        for i in range(len(self.EFF)):
            r += str(self.EFF[i]) + '\n'
        print(r)
    
    
    def get_effective_code(self):
        R_eff = [0]
        for i in range(len(self.INST)-1, 0, -1):
            if self.INST[i].dest not in R_eff:
                self.INST[i].effective = False
                continue
            else:
                if self.INST[i].name in ['Sin','Copy', 'Sqrt', 'Sqr','Exp', 'Log','Not']:
                    if self.INST[i].op1 not in R_eff:
                        R_eff.append(self.INST[i].op1)
                    self.INST[i].effective = True
                elif self.INST[i].name in ['Add', 'Sub', 'Mul', 'Div', 'Lt', 'Gte', 'Eq', 'Neq', 'And', 'Or']:
                    if self.INST[i].op1 not in R_eff:
                        R_eff.append(self.INST[i].op1)
                    if self.INST[i].op2 not in R_eff:
                        R_eff.append(self.INST[i].op2)
                    self.INST[i].effective = True
                elif self.INST[i].name in ['Mean', 'Max', 'Min']:
                    lower = min([self.INST[i].op1, self.INST[i].op2])
                    upper = max([self.INST[i].op1, self.INST[i].op2])
                    for k in range(lower, upper):
                        if k not in R_eff:
                            R_eff.append(k)
                    self.INST[i].effective = True
                elif self.INST[i].name == 'If':
                    if i == len(self.INST)-1:
                        self.INST[i].effective = False
                    elif self.INST[i+1].effective == True:
                        self.INST[i].effective = True
                    else:
                        self.INST[i].effective = False
                R_eff.remove(self.INST[i].dest)
        effective_code = [instruction for instruction in self.INST if instruction.effective == True]
        self.EFF = effective_code
        return effective_code
    
    def execute(self, verbose=False):
        if not self.EFF_UPDATED:
            self.get_effective_code()
            self.EFF_UPDATED = True
        self.EFF.append('END')
        while(self.EFF[self.PC] != 'END'):
            current_instruction = self.EFF[self.PC]
            ret_val, dest_reg   = current_instruction.execute(self.REG)
            if dest_reg >= 0:
                self.REG[dest_reg]  = ret_val
                self.PC += 1
            else:
                if self.EFF[self.PC + 1] == 'END':
                    return self.REG[0]
                dist = 1
                while(self.EFF[self.PC + dist].name == 'If'):
                    dist += 1
                self.PC += 1 + dist #skip to the instruction AFTER the next non-branching instruction
        if(verbose):
            print('______DONE______')
            print('Result: ', self.REG[0])
        self.EFF.remove('END')
        return(self.REG[0])
        
        
class Instruction:
    
    # def __init__(self, name, op1, op2, dest):
    #     self.name = name
    #     self.op1  = op1    #index of register for operand 1
    #     self.op2  = op2    #index of register for operand 2
    #     self.dest = dest   #destination register 
        
    def __init__(self, num_wreg, num_creg, arity=2, num_ireg=1, instruction_set=['Add', 'Sub', 'Mul', 'Div', 'Sin', 'Mean', 'Copy', 'Sqrt', 'Sqr', 'Max', 'Min', 'Exp', 'Log', 'Lt', 'Gte', 'Eq', 'Neq', 'And', 'Or', 'Not', 'If'], _random=True, name="", op1=None, op2=None, dest=None):
        self.name = random.choice(instruction_set)
        self.op1  = random.randint(0, num_wreg+num_creg+num_ireg-1)    #index of register for operand 1
        self.op2  = random.randint(0, num_wreg+num_creg+num_ireg-1)    #index of register for operand 2
        self.dest = random.randint(0, num_wreg-1)                      #destination register
        self.effective = False
        self.num_wreg = num_wreg
        self.num_creg = num_creg
        self.num_ireg = num_ireg
        if not _random:
            self.name = name
            self.op1  = op1
            self.op2  = op2
            self.dest = dest
            
    def _set_name(self, name):
        self.name = name
        
    def _set_op1(self, op):
        if -1< op < self.num_wreg+self.num_creg:
            self.op1 = op
        
    def _set_op2(self, op):
        if -1< op < self.num_wreg+self.num_creg:
            self.op2 = op
            
    def _set_dest(self, op):
        if -1< op < self.num_wreg:
            self.dest = op
        
    def __repr__(self):
        return(self.name + '(' + str(self.op1) + ',' + str(self.op2) + ',' + str(self.dest) + ')')
    
    def _saturate(self, num, low=-1.0*(10**250), high=1.0*(10**250)):
        """ Avoid inf. Can generalize to saturate at other numbers """
        if num > high:
            return high
        if num < low:
            return low
        else:
            return num
    
    def execute(self, register_set):
        """ This can return (return_value, destination_register)  """
        try:
            if self.name == 'Add':
                return (self._saturate(register_set[self.op1] + register_set[self.op2]), self.dest)
            elif self.name == 'Sub':
                return (self._saturate(register_set[self.op1] - register_set[self.op2]), self.dest)
            elif self.name == 'Mul':
                return (self._saturate(register_set[self.op1] * register_set[self.op2]), self.dest)
            elif self.name == 'Div':
                if(register_set[self.op2] == 0):
                    return(register_set[self.dest], self.dest)
                return (self._saturate(register_set[self.op1] / register_set[self.op2]), self.dest)
            elif self.name == 'Sin':
                return (self._saturate(math.sin(register_set[self.op1])), self.dest)
            elif self.name == 'Mean':
                if self.op1 < self.op2:
                    op1 = self.op1
                    op2 = self.op2
                else:
                    op1 = self.op2
                    op2 = self.op1
                l = [register_set[i] for i in range(op1, op2+1)]
                return (self._saturate(statistics.fmean(l)), self.dest)
            elif self.name == 'Copy':
                return (register_set[self.op1], self.dest)
            elif self.name == 'Sqrt':
                if register_set[self.op1] < 0:
                    return (register_set[self.op1], self.dest)
                return (self._saturate(math.sqrt(register_set[self.op1])), self.dest)
            elif self.name == 'Max':
                if self.op1 < self.op2:
                    op1 = self.op1
                    op2 = self.op2
                else:
                    op1 = self.op2
                    op2 = self.op1
                l = [register_set[i] for i in range(op1, op2+1)]
                return (self._saturate(max(l)), self.dest)
            elif self.name == 'Min':
                if self.op1 < self.op2:
                    op1 = self.op1
                    op2 = self.op2
                else:
                    op1 = self.op2
                    op2 = self.op1
                l = [register_set[i] for i in range(op1, op2+1)]
                return (self._saturate(min(l)), self.dest)
            elif self.name == 'Sqr':
                try:
                    ans = (self._saturate(register_set[self.op1]**2), self.dest)
                except OverflowError:
                    ans = (10**10, self.dest)
                return ans
            elif self.name == 'Exp':
                try:
                    ans = (self._saturate(math.exp(register_set[self.op1])), self.dest)
                except OverflowError:
                    ans = (10**10, self.dest)
                return ans
            elif self.name == 'Log':
                if register_set[self.op1] <= 0:
                    return (register_set[self.op1], self.dest)
                return (self._saturate(math.log(register_set[self.op1])), self.dest)
            elif self.name == 'Lt':
                return (float(register_set[self.op1] < register_set[self.op2]), self.dest)
            elif self.name == 'Gte':
                return (float(register_set[self.op1] >= register_set[self.op2]), self.dest)
            elif self.name == 'Eq':
                return (float(register_set[self.op1] == register_set[self.op2]), self.dest)
            elif self.name == 'Neq':
                return (float(register_set[self.op1] != register_set[self.op2]), self.dest)
            elif self.name == 'And':
                return (float(register_set[self.op1] and register_set[self.op2]), self.dest)
            elif self.name == 'Or':
                return (float(register_set[self.op1] or register_set[self.op2]), self.dest)
            elif self.name == 'Not':
                return (float(not register_set[self.op1]), self.dest)
            elif self.name == 'If':
                if(register_set[self.op1]):
                    return (register_set[self.op1], self.op1)
                else:
                    return (register_set[self.op1], -1)
                
        except IndexError:
            print('Index out of Bounds ', self.op1, self.op2, self.dest, self.name)