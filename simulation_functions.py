import numpy as np
from operator import itemgetter

import blockchain as bc

#TODO: this function may be useful in the future: calculate the probability alpha0, alpha1, ... that a block will be appended to a given block 0, 1, ... in the next round
#these functions are outside of the classes because they will be used for the simulation.
#this design decision is more or less arbitrary and could be changed easily

def finalExpectedPayoff(_B, _i):
    #
    #'_B' is a blockchain object
    #'_i' is a miner we want the compute the expected payoff for
    #this function simply computes the expected payoff over all the longest chains in '_B'
    #returns the payoff 'p' of the game if it were to end now (i.e. if '_B' defines the final structure of the game)
    #

    T = _B.horizon
    longest_chains = _B.getLongestChains(T) #this is a list of lists!
    l = len(longest_chains) #number of longest chains

    payoffs = np.array([]) #pre-allocate array for more speed, if needed
    for chain in longest_chains:
        payoffs = np.append(payoffs, _B.getPayoff(_i, chain[-1]))

    p = np.sum(payoffs) / l #each is chain chosen at random with equal probability

    return p



def recursion(_B, _TT, _tt, _t, _i):
    #
    #'_B' is the blockchain we are looking at
    #'_TT' is the extended horizon
    #'_tt' is th enumber of stages we have left until we hit stage '_TT'. if it is equal to 1 we have reached the final stage.
    #'_t' is the height of the block we next append a block at for the extended chain
    #'_i' is the index of the miner we want to compute the payoff for
    #returns the expected payoff of the extended chain 'p' that starts with a block appended at '_t'
    #

    _tt -= 1

    #TODO: optimize the number of function calls. you can ignore most futures, because they will never lead to a new longest chain.
    #for example: if we have a chain {b0, b1, b2, b3} all in sequence (i.e. this is the original chain), and T' equal to 2,
    #then mining at b0 is never optimal because that chain can never grow into a longest chain, even if all future blocks were to be appended in that fork.
    #also, creating a fork is never strictly optimal (it can never lead to a strictly higher payoff than all alternative strategies) and sometimes suboptimal.

    #extend chain by one block at height '_t', while assuming miner '_i' wins.
    #NOTE: why? the function is called under the assumption that miner '_i' wants to know if they should mine at block '_t'. if they do not win, then their decision does not influence their payoff.
    B_ext = bc.ExtendedBlockchain(_B, _i, _t)

    n = B_ext.miners.shape[0]
    prob = [] #list of probabilities


    if _tt > 1: #if we are not in the second-to-last stage
        #NOTE: we want to calculate and return the expected payoff when ending up in the current state of the blockchain in '_TT-_tt'.
        #NOTE: we make use of the decision-relevant payoff principle and assume that the miner wins this round, because if they don't then they do not care where they mine since their decision is inconsequential.

        #call recursion at every block without a child and pick the one with the highest expected payoff.
        expected_payoffs = [] #list of tuples '(t, p)' where 'p' is the expected payoff of mining at block 't' in the extended chain 'BE'
        for t in range(_TT - _tt + 1): #for each block
            #first check if block 't' has a child
            #the payoff can never be larger when creating a fork compared to mining "further down the line". creating a fork can never be the best option.
            #hence, we can ignore mining at blocks with a child.
            childless = True
            for s in range(t+1, _TT - _tt +1):
                if B_ext.sequence[s].parent == t: #if there are no blocks that refer to block 't' as their parent then childless == True
                    childless = False
                    break
            if childless == False:
                continue #skip this block if it has a child

            expected_payoffs.append(recursion(B_ext, _TT, _tt, t, _i)) #call recursion

        p = (1/n) * sum(payoffs[1] for payoffs in expected_payoffs)

        return (_t, p) #return a tuple '(_t, p)' where 'p' is the expected payoff in the state of the blockchain that materializes when mining at '_t'.



    else: #we are in the last stage (_tt == 1), there is only one block left to be appended.
        #NOTE: we want to calculate and return the expected payoff when ending up in the current state of the blockchain in '_TT-1'.

        #NOTE: for each miner get the naive strategy.
        #using that information, calculate every possible end state of the blockchain
        strats = [] #list of lists of strategies, entries are ordered by the index of the miners, i.e. strats[2] is the list of possible strategies of miner with index 2 (the third miner).
        for m in range(n): #for each miner
            #NOTE: in the last stage it is optimal to follow the naive strategy, because then the naive assumption that the game ends after the current stage is correct!
            strats.append(B_ext.getNaiveStrategies(m, _TT - _tt)) #get strategies

        #get possible end-states
        #NOTE: an end-state is uniquely characterized by the index of the block the next block is appended at, together with the miner that won that block.
        end_states = [] #list of tuples '(t, i, prob)' where 't' is the height of the block miner 'i' mined at, and won. 'prob' is the probability that this end state materializes
        for m in range(n): #for each miner
            S = len(strats[m]) #number of viable strategies for miner 'm'
            if S > 1: #if there are multiple (equally good) strategies for miner 'm'
                for s in range(S):
                    prob = 1/n * 1/S #this end state materialzies with probability 1/n * 1/S, since this miner has S strategies to choose from and wins with probability 1/n
                    end_states.append((strats[m][s], m, prob)) #append the end states they are aiming at
            else:
                prob = 1/n  #this end state materialzies with probability 1/n, since the miner only has one strategy to choose from and wins with probability 1/n
                end_states.append((strats[m][0], m, prob)) #append the end state they are aiming at

        #NOTE: for each possible end-state, extend the chain one more time and yield the final expected payoff
        end_state_payoffs = [] #list of payoffs for miner '_i', one for each end state, ordered in the same way as the list 'end_states', i.e. end_state_payoffs[2] corresponds to end_state[2]
        for end_state in end_states:
            #extend the chain BE according to the end-state
            t = end_state[0]
            i = end_state[1]
            prob = end_state[2]
            B_ext2 = bc.ExtendedBlockchain(B_ext, i, t)
            end_state_payoffs.append(finalExpectedPayoff(B_ext2, _i) * prob) #multiply with the probability of materializing to get a probability weighted payoff

        """
        ### PRINTS FOR DEBUGGING ###
        print("strats", strats)
        print("end_states", end_states)
        print("end_state_payoffs", end_state_payoffs)
        """

        #now we can calculate the expected payoff
        p = sum(end_state_payoffs) #sum the probability weighted payoffs

        return (_t, p) #return a tuple '(_t, p)' where 'p' is the expected payoff in the state of the blockchain that materializes when mining at '_t'.




def optimalStrategies(_B, _i, _TT):
    #
    #'_B' is a blockchain object
    #'_i' is a miner we want the compute the optimal strategy for
    #'_TT' is the horizon of the extended chain, the horizon of the extended game starting at '_B.horizon'
    #returns a list of blocks at which miner '_i' should optimally mine to maximize their payoff at the end of the extended game with horizon '_TT', regardless of the miner's strategy
    #each block in the list has the same expected payoff, the miner is indifferent between them
    #

    T = _B.horizon
    n = _B.miners.shape[0]
    tt = _TT - T #number of stages we look into the future

    assert tt > 0, "T'-T must be at least 1"

    expected_payoffs = [] #list of tuples '(t, p)' where 'p' is the expected payoff of mining at block 't' in the base chain
    for t in range(_B.horizon + 1): #for each block
        #first check if block 't' has a child
        #the payoff can never be larger when creating a fork compared to mining "further down the line". creating a fork can never be the best option.
        #hence, we can ignore mining at blocks with a child.
        childless = True
        for s in range(t+1, T+1):
            if _B.sequence[s].parent == t: #if there are no blocks that refer to block 't' as their parent then childless == True
                childless = False
                break
        if childless == False:
            continue #skip this block if it has a child

        expected_payoffs.append(recursion(_B, _TT, tt, t, _i)) #call recursion at a block with no child

    #choose the right blocks to mine at
    max_tup = max(expected_payoffs, key=itemgetter(1))
    max_payoff = max_tup[1]
    blocks = []
    for tup in expected_payoffs:
        if tup[1] == max_payoff:
            blocks.append(tup[0])

    return blocks



