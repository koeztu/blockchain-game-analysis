import numpy as np
import blockchain as bc
import simulation_functions as simfun
import helper_functions as helfun


seed = int(np.random.randint(0, 1000, 1))
print("seed:", seed)
np.random.seed(seed) #seed


#MAIN /////////////////////////////////////////////////////////////////////////////

def main():

    #define variables
    T = 10 #time horizon
    n = 2 #number of players
    p, q, r = 1, 1, 0


    types = np.array([p, q, r])
    #parents = np.array([0, 1, 2, 3, 4, 5, 3, 2, 5, 6])
    #winners = np.array([0, 2, 1, 1, 1, 2, 0, 0, 1, 2])
    parents = helfun.drawParents(T, n)
    winners = helfun.drawWinners(T, n)


    ### ASSERTIONS ###---------------------------------------------------------------------------------------
    assert n == p + q + r, "n must equal p + q + r"
    assert winners.shape[0] == parents.shape[0], "arrays \'parents\' and \'winners\' must be of same length"
    for t in range(T):
        assert winners[t] < np.sum(types), "only miners who exist can win"
        assert parents[t] < t+1, "the parent of a block must have a strictly lower index"
    ###------------------------------------------------------------------------------------------------------

    B = bc.Blockchain(types, parents, winners) #most important line


    #NOTE: uncomment below to print all miners
    for i in range(n):
        B.miners[i].printMiner()


    #NOTE: uncomment below to print all blocks
    """
    for t in range(1, T+1): #for each element in the blockchain
        B.sequence[t].printBlock()
    """


    #draw the blockchain using treelib, just for visualization purposes
    helfun.drawChain(B)
    print("\noriginal chain", B.getOriginalChain(T))
    print("longest chains", B.longestchains)
    print("")

    #NOTE: uncomment below to print some payoffs (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    """
    m = n-1 #the last miner, arbitrarily chosen
    print(f"\npayoff for miner {m} in all chains and subchains:")
    for t in range(T+1):
        print(f"the payoff for the chain ending in block {t} is {B.getPayoff(m, t)}")
    """


    #NOTE: uncomment below to print conservative and longest chain strategies (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    """
    m = n-1 #arbitrary choice
    print("All conservative miners mine at block", B.getConservativeStrategy(T), "in the next stage")
    print(f"Longest-chain miner {m} mines at (one of) the block(s)", B.getLongestChainStrategies(m), "in the next stage")
    """


    #NOTE: uncomment below to test naive miner decision-relevant payoff and strategy (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    """
    m = n-1 #arbitrary choice
    print("will appending at block 2 result in a longest chain?", B.willBeLongestChain(2))
    for t in range(T+1):
        print(f"decision-relevant payoff for naive miner 2 when mining at block {t} is", round(B.getDecisionRelevantPayoff(m, t), 3))
    print(f"the naive miner {m} will mine at (one of) the block(s) in", B.getNaiveStrategies(m, T), "next stage")
    """


    #NOTE: uncomment below to test function 'finalExpectedPayoff' (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    """
    m = n-1 #arbitrary choice
    print(f"final expected payoff for miner {m} is", simfun.finalExpectedPayoff(B, m))
    """


    #NOTE: uncomment below to test blockchain extension (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    """
    m = n-1 #arbitrary choice
    t = T #arbitrary choice
    B_ext = bc.ExtendedBlockchain(B, m, t)
    print("extended chain:")
    for i in range(n):
        B_ext.miners[i].printMiner()
    helfun.drawChain(B_ext)
    """


    #NOTE: uncomment below to test the function 'optimalStrategy' (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    import time
    start = time.process_time()

    m = n-1 #arbitrary choice
    TT = T + 5
    print(f"optimal strategy for miner {m} is to mine at (one of) the block(s)", simfun.optimalStrategies(B, m, TT))

    end = time.process_time()
    print(round((end - start) * 1000, 2), "ms")


    #simfun.testProposition(3, 2, 2+5) #run one test with semi-arbitrary parameters for proposition 1.4
    simfun.testProposition(3, 4, 4+4) #run one test with semi-arbitrary parameters for proposition 1.3

    B.to_csv("./chain.csv")


main()
