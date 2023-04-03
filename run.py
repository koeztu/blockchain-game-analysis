import numpy as np
import blockchain as bc

import helper_functions as helfun
import payoff_matrix as pm
import equilibrium_paths as eq
import time


seed = int(np.random.randint(0, 1000, 1))
#print("seed:", seed)
np.random.seed(seed) #seed


def calcPayoffMatrix():
    #
    #calculates the payoff matrix 
    #parameters need to be specified manually in the function's code below
    #

    #define variables
    T = 5 #time horizon
    n = 2 #number of players

    #generate base chain of length 2
    parents = np.array([0])
    winners = np.array([0]) #w.l.o.g. m0 wins the first stage

    #parents = np.array([0, 0])
    #winners = np.array([0, 1])

    #parents = np.array([0, 0, 2])
    #winners = np.array([0, 1, 1])

    B = bc.Blockchain(n, parents, winners)

    #helfun.drawChain(B)

    start = time.process_time()
    M = pm.intermediatePayoffMatrix(B, T, n)
    end = time.process_time()

    print(M)
    #print(getStrategies(B, T, n))
    print('T =', T)
    print('the payoff-matrix calculation took', round((end - start), 0), "seconds to terminate")
    print("")



def testEqPaths():
    #
    #test all equilibrium paths for forks
    #parameters need to be specified manually in the function's code below
    #

    #define variables
    T = 5 #time horizon
    n = 2 #number of players

    start = time.process_time()
    print('found? ', eq.eqPaths(T, n))
    end = time.process_time()
    
    print('T =', T)
    print('the eq. path check took', round((end - start), 0), "seconds to terminate")
    print("")


#MAIN /////////////////////////////////////////////////////////////////////////////

def main():

    #NOTE: uncomment below to set parameters for testing
    """
    #define variables
    T = 3 #time horizon
    n = 2 #number of players

    parents = helfun.drawParents(T, n)
    winners = helfun.drawWinners(T, n)


    ### ASSERTIONS ###---------------------------------------------------------------------------------------
    assert winners.shape[0] == parents.shape[0], "arrays 'parents' and 'winners' must be of same length"
    for t in range(T):
        assert parents[t] < t+1, "the parent of a block must have a strictly lower index"
    ###------------------------------------------------------------------------------------------------------

    B = bc.Blockchain(n, parents, winners) #most important line
    """


    #NOTE: uncomment below to print all miners
    """
    for i in range(n):
        B.miners[i].printMiner()
    """


    #NOTE: uncomment below to print all blocks
    """
    for t in range(1, T+1): #for each element in the blockchain
        B.sequence[t].printBlock()
    """


    #NOTE: draw the blockchain using treelib, just for visualization purposes
    """
    helfun.drawChain(B)
    print("\noriginal chain", B.getOriginalChain(T))
    print("longest chains", B.longestchains)
    print("")
    """


    #NOTE: uncomment below to print some payoffs
    """
    m = n-1 #the last miner, arbitrarily chosen
    print(f"\npayoff for miner {m} in all chains and subchains:")
    for t in range(T+1):
        print(f"the payoff for the chain ending in block {t} is {B.getPayoff(m, t)}")
    """


    #NOTE: uncomment below to test naive miner decision-relevant payoff and strategy
    """
    m = n-1 #arbitrary choice
    print("will appending at block 2 result in a longest chain?", B.willBeLongestChain(2))
    for t in range(T+1):
        print(f"decision-relevant payoff for naive miner 2 when mining at block {t} is", round(B.getDecisionRelevantPayoff(m, t), 3))
    print(f"the naive miner {m} will mine at (one of) the block(s) in", B.getNaiveStrategies(m, T), "next stage")
    """


    #NOTE: uncomment below to test function 'finalExpectedPayoff'
    """
    m = n-1 #arbitrary choice
    print(f"final expected payoff for miner {m} is", pm.finalExpectedPayoff(B, m))
    """


    #NOTE: uncomment below to test blockchain extension
    """
    m = n-1 #arbitrary choice
    t = T #arbitrary choice
    B_ext = bc.ExtendedBlockchain(B, m, t)
    print("extended chain:")
    for i in range(n):
        B_ext.miners[i].printMiner()
    helfun.drawChain(B_ext)
    """


    #NOTE: uncomment below to test the function 'optimalStrategy'
    """
    print(f"payoff matrix:", pm.payoffMatrix(B, n, T))
    """


    #NOTE: uncomment below to run payoff matrix calculation or equilibirum path check
    calcPayoffMatrix()
    testEqPaths()

main()
