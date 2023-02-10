import numpy as np
import blockchain as bc


np.random.seed(9) #seed


#MAIN /////////////////////////////////////////////////////////////////////////////

def main():

    #define variables
    T = 10 #time horizon
    n = 3 #number of players
    p, q, r = 1, 1, 1
    B = bc.Blockchain(T, n, p, q, r) #most important line

    #NOTE: uncomment below to print all miners
    for i in range(n):
        B.miners[i].printMiner()


    #NOTE: uncomment below to print all blocks
    """
    for t in range(1, T+1): #for each element in the blockchain
        B.sequence[t].printBlock()
    """


    #draw the blockchain using treelib, just for visualization purposes
    from treelib import Tree
    import graphviz

    tree = Tree()
    for t in range(T+1):
        if t == 0:
            tree.create_node(f"b{B.sequence[0].height}", f"{B.sequence[0].height}")
        else:
            tree.create_node(f"b{B.sequence[t].height}", f"{B.sequence[t].height}", parent=f"{B.sequence[t].parent}")

    print("")
    tree.show()

    print("\noriginal chain", B.getOriginalChain(T))
    print("\nlongest chains", B.getLongestChains(T))

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
    print(f"Longest-chain miner {m} mines at block", B.getLongestChainStrategy(m, T), "in the next stage")
    """


    #NOTE: uncomment below to test naive miner decision-relevant payoff and strategy (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    """
    m = n-1 #arbitrary choice
    print("will appending at block 2 result in a longest chain?", B.willBeLongestChain(2))
    for t in range(T+1):
        print(f"decision-relevant payoff for naive miner 2 when mining at block {t} is", round(B.getDecisionRelevantPayoff(m, t), 3))
    print(f"miner {m} will mine at block", B.getNaiveStrategy(m, T), "next stage")
    """

    #NOTE: uncomment below to test function 'finalExpectedPayoff' (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    """
    m = n-1 #arbitrary choice
    print(f"final expected payoff for miner {m} is", bc.finalExpectedPayoff(B, m))
    """

    #NOTE: uncomment below to test the function 'optimalStrategy' (variables at the start of the file i.e. T, n, p, q, and r may need to be adjusted)
    m = n-1 #arbitrary choice
    TT = T + 3 #look two periods into the future
    print(f"optimal strategy for miner {m} is to mine at", bc.optimalStrategy(B, m, TT))



main()
