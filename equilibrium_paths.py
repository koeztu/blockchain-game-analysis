import numpy as np
import itertools
import time

import blockchain as bc
import helper_functions as helfun
import payoff_matrix as pm


seed = int(np.random.randint(0, 1000, 1))
#seed = 650
#print("seed:", seed)
np.random.seed(seed) #seed



def eqPathsGeneral(_T, _n):
    #
    #the general case where we start from an off-path situation
    #'_B' is a blockchain that represents tha starting point of the game that will be played
    #'_T' is the number of stages in the game, including the stages that were already played
    #'_n' is the number of players, which must be 2
    assert _n == 2, "only 2 player games are supported"

    return 0


def eqPaths(_T, _n):
    #
    #the on-path case where we start at t=1
    #'_T' is the number of stages in the game
    #'_n' is the number of players, which must be 2
    assert _n == 2, "only 2 player games are supported"
    assert _T > 2, "go further!"
    #
    #JUST THROW AN ERROR WHEN WE ENCOUNTER MULTIPLE NASH EQ IN A STAGE ON-PATH
    #it doesn't happen for T<=4, and maybe it never will, hence do not worry about that possibility yet.
    #
    #we want to figure out if there is an on-path situation where miners do not mine according to (b_{t-1}, b_{t-1})
    #that would mean that they create a fork
    #if we find a counter-example (i.e. a situation where a miner creates a fork) we can expand the algorithm to tell us what all the eq. paths are. but for the moment I suspect there is only one family of eq. paths, the ones that result in one chain without any forks. I want to test if I am wrong.

    #BUILD BASE CHAIN
    parents = np.array([0])
    winners = np.array([0]) #w.l.o.g. m0 wins the first stage
    B = bc.Blockchain(_n, parents, winners)

    nash_strats = pm.getStrategies(B, _T, _n)
    #no need to check if multiple nash eq here since we are in the second stage only here
    for i in range(_n):
        B_ext = bc.ExtendedBlockchain(B, i, nash_strats[0][i]) #extend chain when 'i' wins
        found = recursion(B_ext, 2, _T, _n) #start in second stage
        if found == True:
            return True

  
    return False


def recursion(_B, _t, _T, _n):
    t = _t + 1
    nash_strats = pm.getStrategies(_B, _T, _n)
    print('nash strategy pair(s):', nash_strats, f'(in stage {t})')
    if len(nash_strats) > 1: #check if multiple nash eq here!
        print('multiple equilibrium strategies found!')
        return True #counter-example with more than one nash-eq (on-path) found
    if t == _T:
        return False #no counter-example found
    for i in range(_n):
        B_ext = bc.ExtendedBlockchain(_B, i, nash_strats[0][i]) #extend chain when 'i' wins
        found = recursion(B_ext, t, _T, _n) #found a counter-example?
        if found == True:
            return True

    return False 




#MAIN /////////////////////////////////////////////////////////////////////////////

def main():

    #define variables
    T = 5 #time horizon
    n = 2 #number of players

    start = time.process_time()

    print('found? ', eqPaths(T, n))

    
    end = time.process_time()
    print('the program took', round((end - start), 0), "seconds to terminate")



#main()
