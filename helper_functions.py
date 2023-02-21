import numpy as np

import blockchain as bc


def drawChain(_B):
    #
    #draw the blockchain to console output for visualisation
    #

    from treelib import Tree
    import graphviz

    T = _B.horizon

    tree = Tree()
    for t in range(T+1):
        if t == 0:
            tree.create_node(f"b{_B.sequence[0].height}", f"{_B.sequence[0].height}")
        else:
            tree.create_node(f"b{_B.sequence[t].height}", f"{_B.sequence[t].height}", parent=f"{_B.sequence[t].parent}")

    print("")
    tree.show()



def drawWinners(_T, _n):
    #
    #draws a winner for each stage 't' in {1, ..., T}
    #updates the miner attribute accordingly
    #and returns an array with the indices of the miners that won in each round
    #

    winners = np.random.randint(0, _n, _T) #winners at each stage, 'winners[t]' is the index of the winning miner of block 't+1'

    return winners



def drawParents(_T, _n):
    #
    #draw random blocks
    #

    parents = np.full(_T, 0)

    for t in range(1, _T):
        parents[t] = np.random.randint(0, t) #strategies for each player in each stage, blocks are randomly chosen

    return parents
