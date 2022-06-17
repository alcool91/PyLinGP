##################################################################################
# Library for selection of generations in genetic programming
#
#
import random
import math
MAX_LENGTH = 36

def set_max_length(new_length):
    global MAX_LENGTH
    MAX_LENGTH=new_length

def I(program, inp):
    """ Interprets program when run on input inp """
    program.reset()
    program._set_input(inp)
    return_val = program.execute()

    return return_val

def mut(program):
    #PROBABILITIES TO
    ADD_P = 0.095   #Add a random instruction in a random location
    REM_P = 0.06   #Delete a random instruction
    NAM_P = 0.009   #Change the name of an instruction (and therefore its type)
    ARG_P = 0.009   #Change an argument of an instruction
    SWP_P = 0.009   #Swap two instructions
    
    if random.random() < ADD_P:  #Add instruction
        if (len(program.INST) < MAX_LENGTH):
            rand_inst = Instruction(len(program.WREG), len(program.CREG), instruction_set=program.IS)
            loc       = random.randint(0, len(program.INST))
            program.INST.insert(loc, rand_inst)
            
    if random.random() < REM_P:  #Remove instruction
        if (len(program.INST) > MIN_LENGTH):
            loc       = random.randint(0, len(program.INST)-1)
            program.INST.pop(loc)
            
    if random.random() < NAM_P:  #Change an instruction name
        if(len(program.INST) > 1):
            loc = random.randint(0, len(program.INST)-1)
            program.INST[loc]._set_name(random.choice(program.IS))
        
    if random.random() < ARG_P:   #Change argument to an instruction
        if(len(program.INST) > 1):
            inst_loc = random.randint(0, len(program.INST)-1)
            arg_loc  = random.randint(0,2)
            if arg_loc == 1:
                program.INST[inst_loc]._set_op1(random.randint(0, len(program.REG)))
            if arg_loc == 2:
                program.INST[inst_loc]._set_op2(random.randint(0, len(program.REG)))
            if arg_loc == 0:
                program.INST[inst_loc]._set_dest(random.randint(0, len(program.WREG)))
            
    if random.random() < SWP_P:   #Swap the index of two instructions
        if (len(program.INST) > 1):
            loc1 = random.randint(0, len(program.INST)-1)
            loc2 = random.randint(0, len(program.INST)-1)
            temp = program.INST[loc1]
            program.INST[loc1] = program.INST[loc2]
            program.INST[loc2] = temp
            
def XOver(prog1, prog2):
    """ Crossover Function chooses 2 random crossover points (one for each individual)
        Swaps the second part of program 2's instructions with the first part of program 1's instructions """
    #TODO: Make sure Xover cannot create programs that are too long!
    #Maybe determine the length of each program after loc1 and loc2 are selected and modify if one would be too long
    length_after_Xover_prog1 = MAX_LENGTH + 1
    length_after_Xover_prog2 = MAX_LENGTH + 1
    
    if ((len(prog1.INST) > 1) and (len(prog2.INST) > 1)):
        while(length_after_Xover_prog1 > MAX_LENGTH or length_after_Xover_prog2 > MAX_LENGTH):
            loc1 = random.randint(0, len(prog1.INST)-1)
            loc2 = random.randint(0, len(prog2.INST)-1)
            temp1 = prog1.INST[:loc1]
            temp2 = prog2.INST[loc2:]
            length_after_Xover_prog1 = len(temp2 + prog1.INST[loc1:])
            length_after_Xover_prog2 = len(prog2.INST[:loc2] + temp1)
        prog1.INST = temp2 + prog1.INST[loc1:]
        prog2.INST = prog2.INST[:loc2] + temp1


def tournament_selection(initial_population, fitness, fitness_cases, opt_max = False, pop_fitnesses=None, next_gen_size=None, k=2, p=1):
    """ 
    initial_population: An array of programs,
    next_gen_size:      Number of individuals to select from the intial population (defaults to the size of initial_population),
    fitness:            Fitness function to use in selection of individuals. Should take a program and set of fitness cases as input.
    fitness_cases:      List of inputs to evaluate fitness on
    pop_fitnesses:      Optionally pass a list of fitnesses of individuals to avoid recomputing them
    opt_max             True if fitter individuals have higher fitness, false if fitter individuals have lower fitness
    k:                  Number of individuals to randomly select for the tournament (default 2)
    p:                  Probability of choosing the best individual (default 1 - deterministic tournament)
    ------------------------------------------------------------------------------------------------------------------------------------
    returns:            A list of programs selected of size next_gen_size
    """
    if next_gen_size == None:
        next_gen_size = len(initial_population)
    if pop_fitnesses == None:
        pop_fitnesses = []
        for individual in initial_population:
            ind_fit = fitness(individual, fitness_cases)
            pop_fitnesses.append(ind_fit)
    #print('Population fitness length: ', len(pop_fitnesses))
    #print('Population length: ', len(initial_population))
    next_gen = []
#    probs   = [p*((1-p)**(k-i-1)) for i in range(k)]
    while len(next_gen) < next_gen_size:
        indxs             = [random.randint(0, len(initial_population)-1) for i in range(k)]
        indxs2             = [random.randint(0, len(initial_population)-1) for i in range(k)]
        #print('indexes: ', indxs)
        fittest           = sorted(indxs, key=lambda x: pop_fitnesses[x], reverse = opt_max)  
        fittest2          = sorted(indxs2, key=lambda x: pop_fitnesses[x], reverse = opt_max)
        #print('fittest: ', fittest)
        i = 0
        winners = []
        tournament_one_winner=False
        tournament_two_winner=False
        while True:
            val1 = random.random()
            val2 = random.random()
            if val1 <= p and not tournament_one_winner:
                winners.append(initial_population[fittest[i]]._clone())
                tournament_one_winner=True
            if val2 <= p:
                winners.append(initial_population[fittest2[i]]._clone())
                tournament_two_winner=True
            if tournament_one_winner and tournament_two_winner:
                break
            i = (i+1) % k
        winners.append(winners[0]._clone())
        winners.append(winners[1]._clone())
        XOver(winners[2], winners[3])
        next_gen = next_gen + winners
    if len(next_gen) > next_gen_size:
        next_gen = next_gen[:next_gen_size]
    return next_gen


def random_selection(initial_population, next_gen_size=None):
    """ 
    initial_population: An array of programs,
    next_gen_size:      Number of individuals to select from the intial population (defaults to the size of initial_population),

    ------------------------------------------------------------------------------------------------------------------------------------
    returns:            A list of programs selected of size next_gen_size
    
    Randomly select individuals (with replacement) from initial population
    """
    if next_gen_size == None:
        next_gen_size = len(initial_population)
    next_gen = []
    while len(next_gen) < next_gen_size:
        next_gen.append(random.choice(initial_population))
    return next_gen

def elite_selection(initial_population, fitness, fitness_cases, opt_max = False, pop_fitnesses=None, k=1):
    """ 
    initial_population: An array of programs,
    next_gen_size:      Number of individuals to select from the intial population (defaults to the size of initial_population),
    fitness:            Fitness function to use in selection of individuals. Should take a program and set of fitness cases as input.
    fitness_cases:      List of inputs to evaluate fitness on
    pop_fitnesses:      Optionally pass a list of fitnesses of individuals to avoid recomputing them
    opt_max             True if fitter individuals have higher fitness, false if fitter individuals have lower fitness
    k:                  Number of fittest individuals to keep (default 1)

    ------------------------------------------------------------------------------------------------------------------------------------
    returns:            A list of programs selected of size next_gen_size
    """
    if pop_fitnesses == None:
        pop_fitnesses = []
        for individual in initial_population:
            ind_fit = 0
            ind_fit = fitness(individual, fitness_cases)
            pop_fitnesses.append(ind_fit)
            
    fittest_pop = sorted(range(len(initial_population)), key=lambda x: pop_fitnesses[x], reverse = opt_max)
    # print('---------------fittest pop--------------')
    # print(fittest_pop[:k])
    # print('----------------fitnesses----------------')
    # print([fitness(initial_population[idx]) for idx in fittest_pop][:k])

    return [initial_population[idx]._clone() for idx in fittest_pop[:k]]