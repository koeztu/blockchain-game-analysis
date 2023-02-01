import numpy as np
from blockchain_v2 import Blockchain


np.random.seed(9) #seed


#MAIN /////////////////////////////////////////////////////////////////////////////

def main():

    #define variables
    T = 9 #time horizon
    n = 6 #number of players
    p, q, r = 2, 2, 2
    B = Blockchain(T, n, p, q, r) #most important line

    for i in range(n):
        B.miners[i].printMiner()


    for t in range(1, T+1): #for each element in the blockchain
        B.sequence[t].printBlock()


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

    m = n-1 #the last miner, arbitrarily chosen
    print(f"\npayoff for miner {m} in all chains and subchains:")
    for t in range(T+1):
        print(f"the payoff for the chain ending in block {t} is {B.getPayoff(m, t)}")






main()
