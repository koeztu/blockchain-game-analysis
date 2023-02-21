import numpy as np
import itertools
from operator import itemgetter
import csv

import helper_functions as helfun
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
    longest_chains = _B.longestchains #this is a list of lists!
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
    #'_tt' is the number of stages to go
    #'_t' is the height of the block we next append a block at for the extended chain 'B_ext'
    #'_i' is the index of the miner we want to compute the payoff for
    #returns the expected payoff of the extended chain 'p' that starts with a block appended at '_t'
    #


    #FIXME: optimize the number of function calls. you can ignore most futures, because they will never lead to a new longest chain.
    #for example: if we have a chain {b0, b1, b2, b3} all in sequence (i.e. this is the original chain), and T' equal to 2,
    #then mining at b0 is never optimal because that chain can never grow into a longest chain, even if all future blocks were to be appended in that fork.
    #also, creating a fork is never strictly optimal (it can never lead to a strictly higher payoff than all alternative strategies) and sometimes suboptimal.


    #extend chain by one block at height '_t', while assuming miner '_i' wins.
    #NOTE: why? the function is called under the assumption that miner '_i' wants to know if they should mine at block '_t'. if they do not win, then their decision does not influence their payoff.
    B_ext = bc.ExtendedBlockchain(_B, _i, _t)
    _tt -= 1 #decrement the number of stages to go, now '_tt' is equal to the number of stages left after this one
    n = B_ext.miners.shape[0]
    prob = [] #list of probabilities


    if _tt > 1: #if we are not in the second-to-last stage
        #NOTE: we want to calculate and return the expected payoff when ending up in the current state of the blockchain in '_TT-_tt'.
        #NOTE: we make use of the decision-relevant payoff principle and assume that the miner wins this round, because if they don't then they do not care where they mine since their decision is inconsequential.

        #call recursion at every block without a child and pick the one with the highest expected payoff.
        expected_payoffs = [] #list of tuples '(t, p)' where 'p' is the expected payoff of mining at block 't' in the extended chain 'B_ext'
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

        #get the highest payoff the miner can expect
        max_tup = max(expected_payoffs, key=itemgetter(1))
        max_payoff = max_tup[1]
        #FIXME: returning the maximum payoff leads to irrational strategies
        #why? calculating it this way assumes that the miner wins all subsequent stages. this results in indifference between chains that are not equal in length,
        #even tough the miner has the same number of blocks mined in each
        #it should be strictly optimal in this case to mine on the longer chain
        #the approach itself makes sense, it's just that we forget to exclude some obviously suboptimal strategies. the fix is to be found in the parent function 'optimalStrategies()'


        return (_t, max_payoff) #return a tuple '(_t, p)' where 'p' is the highest expected payoff in the state of the blockchain that materializes when mining at '_t'.



    else: #if _tt == 1
        #NOTE: we want to calculate and return the expected payoff when ending up in the current state of the blockchain in '_TT-1'.

        #for each miner get the naive strategy.
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

        #for each possible end-state, extend the chain one more time and yield the final expected payoff
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


    #NOTE: when we have less than 2, i.e. 1, stage to go, we should just call getNaiveStrategies() instead, hence the assertion
    #the recursion function assumes that we always have at least 2 stages to go
    assert tt >= 2, "T'-T must be at least 2, consider calling 'getNaiveStrategies(...)' instead"

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

    #the list 'blocks' includes blocks where the decision-relevant payoff for miner is equal, however, some blocks are strictly inferior because their chain is shorter
    #we need to remove those blocks from the list.
    #NOTE: we need this fix because in all future stages we assume the miner makes their decision under the assumption that they win. this leads to indifference between blocks that do not yield the same expected payoff.
    #FIXME: this function may have to be re-written becuase that assumption above may not make sense *when repeated multiple times* (but it is correct for the naive decision problem)


    chainlength = [] #list that stores the length of each chain ending in the blocks in the list 'blocks', 'chainlength[1]' is the length of the chain ending in 'blocks[1]'
    for block in blocks:
        length = 0
        while _B.sequence[block].genesis != True:
            length += 1
            block = _B.sequence[block].parent
        chainlength.append(length)


    blocks = np.array(blocks)
    maxima = chainlength == np.max(chainlength) #create mask of the highest chains


    return blocks[maxima]


def testProposition(_n, _T, _TT):
    #
    #setup:
    #   we have 'n' miners
    #   miner 'n' with index 'n-1' does not win any blocks up to and including stage 'T'
    #   they play optimally in stage 'T+1' and win
    #   NOTE: playing optimally when one has not won any blocks yet means mining on one of the longest chains
    #   the game last until stage 'TT > T'
    #   all miners play optimally, their types are irrelevant
    #
    #question:
    #   is it always optimal for miner 'i' to mine on the branch they won their first block in, in the following intermediate stage T+2?
    #
    #parameters of the simulation:
    #   'n', number of opponent miners
    #   'T', height of the base chain
    #   'tt', number of intermediate stages until the game ends
    #   'TT = T + tt', horizon of the extended chain
    #

    #NOTE: one could search simultaneously different parts of the search-space to speed up the search since one python script only runs on one core.
    #I have 12 cores available to me, so I could launch 12 parallel searches.

    tt = _TT - _T

    #NOTE: we only have to look at the case where miner 'n-1' loses all subsequent intermediate stages
    #why? because if they won another round, then that would only strengthen their resolve of mining on this branch.

    #NOTE: we must generate some off-path situation (some base chain of horizon T) and then check for every subsequent stage if it is still optimal to keep mining on the same branch.
    #the miner will be facing a mixture of conservative, longest-chain, and naive miners
    #the extended game starts at some off-path situation and continues according to the miner's strategies (and random chance, but we simualte all possible sitautions so random chance does not get to play a role here).
    #we therfore only consider 'on-path' futures that branch off of the off-path base chain.


    possible_types = [] #list of lists of types
    possible_parents = [] #list of lists of parents
    possible_winners = [] #list of lists of winners

    #generate every combination of types
    types = [np.nan, np.nan, np.nan]
    for p in range(_n+1):
        q = 0
        while p + q <= _n:
            types[0] = p
            types[1] = q
            types[2] = _n-p-q #r
            possible_types.append(types)
            q += 1
            types = [np.nan, np.nan, np.nan]


    #generate every combination of parents
    blocks = np.arange(_T)

    for element in itertools.product(blocks, repeat=_T):
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
    miners = np.arange(_n)
    for combination in itertools.combinations_with_replacement(miners, _T):
        possible_winners.append(list(combination))


    #add the miner who just enters the game to the type list
    #FIXME: this may not be necessary, but not sure
    for i in range(len(possible_types)):
        possible_types[i][1] += 1 #the last miner is defined as a longest chain miner because their strategy is to mine at the longest chain since they have not won any blocks yet


    #for all possible base chains:
    possible_types = np.array(possible_types)
    possible_parents = np.array(possible_parents)
    possible_winners = np.array(possible_winners)
    tt -= 1
    iteration = 0
    for types in possible_types:
        for parents in possible_parents:
            for winners in possible_winners:
                iteration +=1
                if iteration % 2000 == 0:
                    print('base chain number', iteration)
                #print('types', types, 'parents', parents, 'winners', winners)
                i = _n #the new miner has index '_n'
                b = _T + 1
                B = bc.Blockchain(types, parents, winners)
                optimal_strategies = optimalStrategies(B, i, _TT) #FIXME: this could be sped up, the optimal strategy is to mine at one of the longest chains!
                for optimal_strategy in optimal_strategies:
                    #extend chain when miner n-1 wins (they win their first block in T+1 by assumption)
                    B_ext = bc.ExtendedBlockchain(B, i, optimal_strategy)
                    result = recursion2(B_ext, _TT, tt, b, i)
                    if result[0] == True:
                        #print the result as a tree and to csv
                        B.to_csv("./base_chain.csv")
                        result[1].to_csv("./extended_chain.csv")
                        to_csv("./other_info.csv", result[2], _n, _T, _TT, result[1].horizon)
                        print("base chain:")
                        helfun.drawChain(B)
                        print("extended chain:")
                        helfun.drawChain(result[1])
                        print("the optimal strategies are", result[2])
                        print("the counter-example is caused by mining at block", result[3])
                        print("our miner has index", i)
                        return 0
                #print("found none in this iteration")




def recursion2(_B, _TT, _tt, _b, _i):
    #'_B' is the extended blockchain we are looking at
    #'_TT' is the extended horizon
    #'_tt' is the number of stages to go
    #'_n' is the number of miners in the game
    #'_b' is index of the block miner 'n-1' won in stage 'T + 1'
    #'_i' is the index of the miner we care about
    #
    #returns a list 'result' where;
    #   result[0] is either True if we found a counter-example, False otherwise
    #   result[1] is a blockchain object of the extended chain where it is no longer optimal to mine on the same branch
    #   result[2] is a list of optimal strategies for miner '_i' in that extended chain
    #


    _tt -= 1
    if _tt == 0: #there is no next stage
        return [False, np.nan, np.nan] #return a negative result (no counter example found)


    for miner in _B.miners:
        if miner.number == _i: #skip miner '_i'
            continue
        if miner.conservative == True:
            strats = _B.getConservativeStrategy()
        if miner.longestchain == True:
            strats = _B.getLongestChainStrategies(miner.number)
        if miner.naive == True:
            strats = _B.getNaiveStrategies(miner.number, _B.horizon)
        for strat in strats:
            #NOTE: 'optimal_strategies' are the strategies of the miner we care about, 'strats' are the strategies of some other miner
            B_ext = bc.ExtendedBlockchain(_B, miner.number, strat)

            if _tt == 1: #we have to call getNaiveStrategies when _tt < 2, because optimalStrategies is made for time horizons of at least 2 only
                optimal_strategies = B_ext.getNaiveStrategies(_i, B_ext.horizon)
            else:
                optimal_strategies = optimalStrategies(B_ext, _i, _TT)

            for optimal_strategy in optimal_strategies:
                if isOnSameBranch(B_ext, _b, optimal_strategy): #do we have a counter-example?
                    result = recursion2(B_ext, _TT, _tt, _b, _i)  #call recursion and forward the result back up the chain
                    if result[0] == True:
                        return result
                    else:
                        continue
                else:
                    #we have found a counter example!
                    #return relevant info so it can be printed and saved
                    #print("found a 'fake' counter-example, continuing...")
                    if len(optimal_strategies) == 1:
                        #we only have a 'real' counter example if mining on the same branch is strictly suboptimal,
                        #i.e. when there is only one strategy, which is to mine on some other branch
                        print(B_ext.getNaiveStrategies(_i, B_ext.horizon))
                        print("found a 'real' counter-example")
                        return [True, B_ext, optimal_strategies, optimal_strategy]


    return [False, np.nan, np.nan] #return a negative result (no counter example found)




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
