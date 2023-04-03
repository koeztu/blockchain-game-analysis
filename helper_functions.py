import numpy as np
import csv
from treelib import Tree
import graphviz

import blockchain as bc


def drawChain(_B):
    #
    #draw the blockchain to console output for visualisation
    #

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
        parents[t] = np.random.randint(0, t+1) #strategies for each player in each stage, blocks are randomly chosen

    return parents



def isOnSameBranch(_B, _b, _c):
    #
    #simply checks if two blocks are on the same branch in the blockchain'_B',
    #i.e. if we can get to block '_b' by jumping from parent to parent starting from block '_c'
    #

    isOnSameBranch = False
    t = _c

    while _B.sequence[t].genesis != True:
        if _B.sequence[t].parent == _b:
            isOnSameBranch = True
            break
        else:
            t = _B.sequence[t].parent

    if _b == _c: #trivial case
        isOnSameBranch = True

    return isOnSameBranch


def to_csv(_filename, _optimal_strategies, _n, _T, _TT, _horizon):

    file = open(_filename, 'w')
    writer = csv.writer(file)

    row = [f"optimal strategies in stage {_horizon}"]
    for strategy in _optimal_strategies:
        row.append(strategy)
    writer.writerow(row)

    row = ["number of players"]
    row.append(_n)
    writer.writerow(row)

    row = ["base chain height"]
    row.append(_T)
    writer.writerow(row)

    row = ["extended chain horizon"]
    row.append(_TT)
    writer.writerow(row)


    file.close()
