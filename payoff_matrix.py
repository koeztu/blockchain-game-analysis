import numpy as np
import itertools
import time

import blockchain as bc
import helper_functions as helfun

#NOTE: we can check that the code returns the correct results for T<=3. we also did some checks for T=4, but not for all possibilities, just the ones that could likely contain errors (cases where there are multiple nash eq. off-path). 
#for all T>4 we have to assume the code returns correct results. 


seed = int(np.random.randint(0, 1000, 1))
#seed = 650
#print("seed:", seed)
np.random.seed(seed) #seed


def finalExpectedPayoff(_B, _i):
    #
    #'_B' is a blockchain object
    #'_i' is a miner we want the compute the expected payoff for
    #this function simply computes the expected payoff over all the longest chains in '_B'
    #returns the payoff 'p' of the game if it were to end now (i.e. if '_B' defines the final structure of the game)
    #

    T = _B.horizon
    longest_chains = _B.longestchains #this is a list of lists!
    l = len(longest_chains) #number of longest chains

    payoffs = np.array([]) #pre-allocate array for more speed, if needed
    for chain in longest_chains:
        payoffs = np.append(payoffs, _B.getPayoff(_i, chain[-1]))

    p = np.sum(payoffs) / l #each is chain chosen at random with equal probability

    return p


def intermediatePayoffMatrix(_B, _T, _n):
    #
    #calculates the payoff matrix for an intermediate stage of the multi-stage normal form simultaneous game 
    #with '_n' players which starts with blockchain '_B' and ends at stage '_T'
    #


    t = _B.horizon + 1

    strats = np.arange(t)
    M = np.zeros((t, t, _n))

    if _T == t: #we have reached the final stage
        M = finalPayoffMatrix(_B, _n, t)

    else: #otherwise we need backwards induction from the last stage t=T to get the payoffs for the current stage
        for strat0 in strats:
            for strat1 in strats:
                B_ext0 = bc.ExtendedBlockchain(_B, 0, strat0) #m0 wins
                B_ext1 = bc.ExtendedBlockchain(_B, 1, strat1) #m1 wins
                M_ext0 = intermediatePayoffMatrix(B_ext0, _T, _n)
                M_ext1 = intermediatePayoffMatrix(B_ext1, _T, _n)
                nash0 = matrixNashEq(M_ext0)
                nash1 = matrixNashEq(M_ext1)
                #we are only interested in equilibira in pure strategies for now
                #NOTE: *ASSUMPTION* when there are multiple nash eq., each will materialize with equal probability. 
                #the expected payoff therfore is the probability weighted sum of the nash eq. payoffs
                n_eq0 = np.count_nonzero(nash0) #number of nash eq.
                n_eq1 = np.count_nonzero(nash1)
                M[strat0, strat1, 0] = 0.5 * (M_ext0[nash0].sum(axis=0)[0]/n_eq0 + M_ext1[nash1].sum(axis=0)[0]/n_eq1) #payoff for m0
                M[strat0, strat1, 1]  = 0.5 * (M_ext0[nash0].sum(axis=0)[1]/n_eq0 + M_ext1[nash1].sum(axis=0)[1]/n_eq1) #payoff for m1

    return M



def matrixNashEq(_M):
    #
    #finds the nash eq. of the payoff matrix '_M'
    #find mutual best responses!
    #

    t = _M.shape[0]
    best_responses0 = []
    best_responses1 = []

    for i in range(t):
        row = _M[:, i, 0]
        col = _M[i, :, 1]
        best_responses0.append(row == row.max())
        best_responses1.append(col == col.max())

    nash_eq = np.full((_M.shape[0], _M.shape[1]), False) #mask with 'True' where we have a nash eq.

    for r in range(t): #rows
        for c in range(t): #cols
            if (best_responses0[c][r] == True) and (best_responses1[r][c] == True):
                nash_eq[r,c] = True

    return nash_eq


def finalPayoffMatrix(_B, _n, _t):
    #
    #calculates the payoff matrix of the normal form simultaneous game with '_n' players at stage '_t' with blockchain '_B'
    #

    M = np.zeros((_t, _t, _n))

    for r in range(_t): #rows, blocks m0 can mine at
        for c in range(_t): #cols, blocks m1 can mine at
            B_ext1 = bc.ExtendedBlockchain(_B, 0, r) #m0 wins
            B_ext2 = bc.ExtendedBlockchain(_B, 1, c) #m1 wins
            M[r, c, 0] = 0.5 * (finalExpectedPayoff(B_ext1, 0) + finalExpectedPayoff(B_ext2, 0)) #payoff for m0
            M[r, c, 1] = 0.5 * (finalExpectedPayoff(B_ext1, 1) + finalExpectedPayoff(B_ext2, 1)) #payoff for m1

    return M


def getStrategies(_B, _T, _n):
    #
    #determines the nash eq. strategies of miner '_i' given some blockchain '_B' and game horizon '_T'
    #returns a list of tuples containing the equilibirum strategies
    #nash_strats[0][1] is the strategy of the second [1] miner in the first [0] equilibirum

    M = intermediatePayoffMatrix(_B, _T, _n)
    nash = matrixNashEq(M)
    nash_strats = np.transpose(np.where(nash == True))
    nash_strats = [tuple(element) for element in nash_strats] #convert to tuples

    return nash_strats


#MAIN /////////////////////////////////////////////////////////////////////////////

def main():

    #define variables
    T = 4 #time horizon
    n = 2 #number of players

    #generate base chain of length 2

    #parents = np.array([0])
    #winners = np.array([0]) #w.l.o.g. m0 wins the first stage

    #parents = np.array([0, 0])
    #winners = np.array([0, 1])

    parents = np.array([0, 0, 2])
    winners = np.array([0, 1, 1])


    B = bc.Blockchain(n, parents, winners)

    helfun.drawChain(B)

    start = time.process_time()
    M = intermediatePayoffMatrix(B, T, n)

    end = time.process_time()

    print(M)
    print(getStrategies(B, T, n))

    print('T=', T)
    print('the program took', round((end - start), 0), "seconds to terminate")

#main()
