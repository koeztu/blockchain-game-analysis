import numpy as np
import blockchain as bc
import itertools
import time

import helper_functions as helfun
import payoff_matrix as pm
import equilibrium_paths as eq





def checkSwitching():
    #check if there are situations where a miner ever switches to a shorter branch
    #for this purpose it generates EVERY chain of lengths t=1,2,..., T-1 that is possible in a T stage game, then computes both miner's strategies,
    #and compares them to their strategies in the subsequent stage
      
    #define variables
    T = 5 #time horizon
    n = 2 #number of players


    for t in range(1, T-1):

        possible_parents = [] #list of lists of parents
        possible_winners = [] #list of lists of winners

        #generate every combination of parents
        blocks = np.arange(t)
        for element in itertools.product(blocks, repeat=t): #FIXME: this way of generating all possible parents is very slow for large chains of height greater than ~8, this is beacuse of slow python loops
            #check if element is legal
            legal = True
            for i in range(len(element)):
                if element[i] > i: #parent must have strictly lower index
                    legal = False
                    break
            if legal == False:
                continue

            possible_parents.append(list(element)) #append legal combination

        #generate every combination of winners
        miners = np.arange(n)
        for combination in itertools.combinations_with_replacement(miners, t):
            for permutation in itertools.permutations(combination, t):
                if permutation[0] == 1: #w.l.o.g. m0 wins the first stage, hence a situation where m1 wins is skipped
                    #we just need to make sure to check the strategies for BOTH miners later, since we exclude half the game-tree here
                    continue
                possible_winners.append(list(permutation))

        #for all possible base chains:
        possible_parents = np.array(possible_parents)
        possible_winners = np.array(possible_winners)
        possible_winners = np.unique(possible_winners, axis=0) #kick duplicate entries from array, this is needed because the permutations consider winning stage 2 and stage 1 different from winning stage 1 and stage 2, even tough they are in fact the same

        iteration = 0
    

        for parents in possible_parents:
            for winners in possible_winners:
                B = bc.Blockchain(n, parents, winners)

                print(parents)

                """ 
                ### DEBUG PRINTS ###
                for i in range(n): 
                    B.miners[i].printMiner()
                helfun.drawChain(B)
                """ 
              
                M = pm.intermediatePayoffMatrix(B, T, n)

                nash = pm.matrixNashEq(M) #get a mask of nash equilibria
                nash_strats = np.transpose(np.where(nash == True)) #get the strategy profiles
                nash_strats = np.array([np.array(element) for element in nash_strats]) #convert to np.array



                for strat in nash_strats: #for every possible nash equilibrium

                    B_ext0 = bc.ExtendedBlockchain(B, 0, strat[0]) #extend the chain if m0 won
                    B_ext1 = bc.ExtendedBlockchain(B, 1, strat[1])

                    M_ext0 = pm.intermediatePayoffMatrix(B_ext0, T, n) #payoff matrix if m0 won
                    M_ext1 = pm.intermediatePayoffMatrix(B_ext1, T, n)

                    #get the strategies for the two cases
                    nash0 = pm.matrixNashEq(M_ext0)
                    nash_strats0 = np.transpose(np.where(nash0 == True))
                    nash_strats0 = np.array([np.array(element) for element in nash_strats0])
                    nash1 = pm.matrixNashEq(M_ext1)
                    nash_strats1 = np.transpose(np.where(nash1 == True))
                    nash_strats1 = np.array([np.array(element) for element in nash_strats1])

                    #compare length of chains the miners mine at
                    length_before_m0 = B.chainLength(strat[0]) #get length of chain where m0 mined at before
                    length_before_m1 = B.chainLength(strat[1]) #get length of chain where m1 mined at before

                    #compare that to length of chains where they may mine at now for both cases
                    for strat0 in nash_strats0: #the case where m0 won
                        if B_ext0.chainLength(strat0[0]) < length_before_m0:
                            print("Found a counter-example!")
                            return 0
                        if B_ext0.chainLength(strat0[1]) < length_before_m1:
                            print("Found a counter-example!")
                            return 0

                    for strat1 in nash_strats1: #the case where m1 won
                        if B_ext1.chainLength(strat1[0]) < length_before_m0:
                            print("Found a counter-example!")
                            return 0
                        if B_ext1.chainLength(strat1[1]) < length_before_m1:
                            print("Found a counter-example!")
                            return 0


                iteration += 1
                print(f"checked chain number {iteration} for t = {t+1} and  T = {T}") #'t+1' because 't' in the code above is the number of stages that have passed for the base chain 'B'


        
def checkFirstBlock():
    #check if there are situations where a miner ever switches away from the branch they won their first block on
    #for this purpose it generates EVERY chain where ONLY ONE miner won any blocks on of lengths t=1,2,..., T-1 that are possible in a T stage game, 
    #then computes the other miner's strategy, iterates through the game according to nash equilibrium strategies and checks after each stage if that miner switched away
      
    #define variables
    T = 4 #time horizon
    n = 2 #number of players

    for t in range(1, T-1):

        possible_parents = [] #list of lists of parents
        winners = np.zeros(t) #generate a history where only one miner (w.l.o.g. m0) won any rounds

        #generate every combination of parents
        blocks = np.arange(t)
        for element in itertools.product(blocks, repeat=t): #FIXME: this way of generating all possible parents is very slow for large chains of height greater than ~8
            #check if element is legal
            legal = True
            for i in range(len(element)):
                if element[i] > i: #parent must have strictly lower index
                    legal = False
                    break
            if legal == False:
                continue

            possible_parents.append(list(element)) #append legal combination


        #for all possible base chains:
        possible_parents = np.array(possible_parents)

        iteration = 0
    

        for parents in possible_parents:
            B = bc.Blockchain(n, parents, winners)

            """ 
            ### DEBUG PRINTS ###
            for i in range(n): 
                B.miners[i].printMiner()
            helfun.drawChain(B)
            """ 
            
            M = pm.intermediatePayoffMatrix(B, T, n)

            nash = pm.matrixNashEq(M) #get a mask of nash equilibria
            nash_strats = np.transpose(np.where(nash == True)) #get the strategy profiles
            nash_strats = np.array([np.array(element) for element in nash_strats]) #convert to np.array


            for strat in nash_strats: #for every possible nash equilibrium
                found = recursion(B, T, 1, strat[1], B.horizon + 1) #call recursion when m1 wins their first block
                if found == True:
                    print("Found counter-example!")
                    return 0


            iteration += 1
            print(f"checked chain number {iteration} for t = {t+1} and T = {T}") #'t+1' because 't' in the code above is the number of stages that have passed for the base chain 'B'




def recursion(_B, _T, _i, _t, _c):        
    #
    #'_B' is the blockchain of the last stage
    #'_T' is the number of stages in the game
    #'_i' is the index of the winning miner
    #'_t' is the index of the block the winner chose
    #'_c' is the index of the first block miner 1 won.


    B_ext = bc.ExtendedBlockchain(_B, _i, _t) #extend the chain if mi won

    if B_ext.horizon == _T: #we have reached the end of the game
        return False

    M_ext = pm.intermediatePayoffMatrix(B_ext, _T, 2)

    nash = pm.matrixNashEq(M_ext) #get a mask of nash equilibria
    nash_strats = np.transpose(np.where(nash == True)) #get the strategy profiles
    nash_strats = np.array([np.array(element) for element in nash_strats]) #convert to np.array


    found = False
    for strat in nash_strats: #for every possible nash equilibrium

        #check if we found a counter-example
        found = not helfun.isOnSameBranch(B_ext, _c, strat[1])
        if found == True:
            break

        #else, go deeper

        found = recursion(B_ext, _T, 0, strat[0], _c) #m0 wins
        if found == True:
            break

        found = recursion(B_ext, _T, 1, strat[1], _c) #m1 wins
        if found == True:
            break


    return found





def checkMonotonicity():
    #check if there are situations where monotonicity is violated
    #for this purpose it generates EVERY chain of lengths t=1,2,..., T-1 that is possible in a T stage game, then computes both miner's strategies,
    #and compares them to their strategies in the subsequent stage
      
    #define variables
    T = 6 #time horizon
    n = 2 #number of players


    for t in range(1, T-1):

        possible_parents = [] #list of lists of parents
        possible_winners = [] #list of lists of winners

        #generate every combination of parents
        blocks = np.arange(t)
        for element in itertools.product(blocks, repeat=t): #FIXME: this way of generating all possible parents is very slow for large chains of height greater than ~8, this is beacuse of slow python loops
            #check if element is legal
            legal = True
            for i in range(len(element)):
                if element[i] > i: #parent must have strictly lower index
                    legal = False
                    break
            if legal == False:
                continue

            possible_parents.append(list(element)) #append legal combination

        #generate every combination of winners
        miners = np.arange(n)
        for combination in itertools.combinations_with_replacement(miners, t):
            for permutation in itertools.permutations(combination, t):
                if permutation[0] == 1: #w.l.o.g. m0 wins the first stage, hence a situation where m1 wins is skipped
                    #we just need to make sure to check the strategies for BOTH miners later, since we exclude half the game-tree here
                    continue
                possible_winners.append(list(permutation))

        #for all possible base chains:
        possible_parents = np.array(possible_parents)
        possible_winners = np.array(possible_winners)
        possible_winners = np.unique(possible_winners, axis=0) #kick duplicate entries from array, this is needed because the permutations consider winning stage 2 and stage 1 different from winning stage 1 and stage 2, even tough they are in fact the same

        iteration = 0

        for parents in possible_parents:
            for winners in possible_winners:
                B = bc.Blockchain(n, parents, winners)

                """ 
                ### DEBUG PRINTS ###
                for i in range(n): 
                    B.miners[i].printMiner()
                helfun.drawChain(B)
                """ 
              
                M = pm.intermediatePayoffMatrix(B, T, n)

                nash = pm.matrixNashEq(M) #get a mask of nash equilibria
                nash_strats = np.transpose(np.where(nash == True)) #get the strategy profiles
                nash_strats = np.array([np.array(element) for element in nash_strats]) #convert to np.array


                for strat in nash_strats: #for every possible nash equilibrium

                    B_ext0 = bc.ExtendedBlockchain(B, 0, strat[0]) #extend the chain if m0 won
                    B_ext1 = bc.ExtendedBlockchain(B, 1, strat[1])

                    M_ext0 = pm.intermediatePayoffMatrix(B_ext0, T, n) #payoff matrix if m0 won
                    M_ext1 = pm.intermediatePayoffMatrix(B_ext1, T, n)

                    #get the strategies for the two cases
                    nash0 = pm.matrixNashEq(M_ext0)
                    nash_strats0 = np.transpose(np.where(nash0 == True))
                    nash_strats0 = np.array([np.array(element) for element in nash_strats0])
                    nash1 = pm.matrixNashEq(M_ext1)
                    nash_strats1 = np.transpose(np.where(nash1 == True))
                    nash_strats1 = np.array([np.array(element) for element in nash_strats1])


                    #compare strategies to see if any miner keeps mining on b_s in stage t+1
                    #also check if the parent of the most recent block is equal to the strategy, only then are we in a situation where monotonicity can be violated,
                    #because then we have bs <- bt
                    for strat0 in nash_strats0: #the case where m0 won
                        if strat0[0] == strat[0] and strat0[0] == B_ext0.sequence[-1].parent:
                            print("Found a counter-example! 1")
                            return 0
                        if strat0[1] == strat[1] and strat0[1] == B_ext0.sequence[-1].parent:
                            if strat0[1] == B_ext0.sequence[-1].parent:
                                print("Found a counter-example! 2")
                                """
                                print(strat0[1])
                                print(B_ext0.sequence[-1].parent)
                                for i in range(n): 
                                    B_ext0.miners[i].printMiner()
                                helfun.drawChain(B)
                                helfun.drawChain(B_ext0)
                                """
                            return 0

                    for strat1 in nash_strats1: #the case where m1 won
                        if strat1[0] == strat[0] and strat1[0] == B_ext1.sequence[-1].parent:
                            print("Found a counter-example! 3")
                            return 0
                        if strat1[1] == strat[1] and strat1[1] == B_ext1.sequence[-1].parent:
                            print("Found a counter-example! 4")
                            return 0


                iteration += 1
                print(f"checked chain number {iteration} for t = {t+1} and  T = {T}") #'t+1' because 't' in the code above is the number of stages that have passed for the base chain 'B'




def main():

    #define variables
    T = 4 #time horizon
    n = 2 #number of players

    start = time.process_time()

    #NOTE: uncomment the test you wish to run. the parameters (T and n) need to be set in the function's code above at the moment
    #checkSwitching()
    #checkFirstBlock()
    #checkMonotonicity()

    end = time.process_time()
    print('the program took', round((end - start), 0), "seconds to terminate")
    
main()