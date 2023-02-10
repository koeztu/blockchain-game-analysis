import numpy as np
from operator import itemgetter

#TODO: function for calculating optimal strategy (which block to mine at) for any stage 't' and for any miner 'i' (HARD)
#TODO: this function may be useful in the future: calculate the probability alpha0, alpha1, ... that a block will be appended to a given block 0, 1, ... in the next round

#FUNCTIONS ////////////////////////////////////////////////////////////////////////////////////////////////////
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
    B_ext = _B.copyAndExtend(_i, _t)

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
        strats = [] #list of strategies, entries are ordered by the index of the miners, i.e. strats[2] is the strategy of miner with index 2 (the third miner).
        for m in range(n): #for each miner
            #NOTE: in the last stage it is optimal to follow the naive strategy, because then the naive assumption that the game ends after the current stage is correct!
            strats.append(B_ext.getNaiveStrategy(m, _TT - _tt)) #get strategies
            #FIXME: the function getNaiveStrategy() chooses one block at random if two blocks have the same expected payoff. this is not what we want here!
            #we want to know that there are two blocks with the same expected payoff, and incorporate that into the payoff calculation below.

            """
            ### UNFINISHED ###
            potential_strategies = BE.getAllNaiveStrategies(m, _TT-_tt)
            if len(strategies) == 1: #if there is only one dominant strategy
                strats.append((potential_strategies, 1/n)) #this strategy will be played with probability of 1 and win with probability 1/n
            else: #if there are more than one equally good strategies
                for strategy in potential_strategies:
                    strats.append((strategy, 1/len(potential_strategies) * 1/n)) #this strategy will be played with probability of 1/len(potential_strategies) and win with probability 1/n, given that it was played
            """


        #NOTE: get possible end-states
        #an end-state is uniquely characterized by the index of the block the next block is appended at, together with the miner that won that block.
        end_states = [] #list of tuples '(t, i)' where 't' is the height of the block miner 'i' mined at, and won.
        for m in range(n): #for each miner
            end_states.append((strats[m], m)) #append the end state they are aiming at


        #NOTE: for each possible end-state, extend the chain one more time and yield the final expected payoff
        end_state_payoffs = [] #list of payoffs for miner '_i', one for each end state, ordered in the same way as the list 'end_states', i.e. end_state_payoffs[2] corresponds to end_state[2]
        for end_state in end_states:
            #extend the chain BE according to the end-state
            t = end_state[0]
            i = end_state[1]
            B_ext2 = B_ext.copyAndExtend(i, t)
            end_state_payoffs.append(finalExpectedPayoff(B_ext2, _i))

        """
        ### PRINTS FOR DEBUGGING ###
        print("strats", strats)
        print("end_states", end_states)
        print("end_state_payoffs", end_state_payoffs)
        """

        #NOTE: now we can calculate the expected payoff
        #each end_state materializes with probability 1/n.

        p = (1/n) * sum(end_state_payoffs)

        return (_t, p) #return a tuple '(_t, p)' where 'p' is the expected payoff in the state of the blockchain that materializes when mining at '_t'.




def optimalStrategy(_B, _i, _TT):
    #
    #'_B' is a blockchain object
    #'_i' is a miner we want the compute the optimal strategy for
    #'_TT' is the horizon of the extended chain, the horizon of the extended game starting at '_B.horizon'
    #returns the block 't' at which miner '_i' should optimally mine to maximize their payoff at the end of the extended game with horizon '_TT', regardless of the miner's strategy
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

    #choose the right block to mine at, return it
    #FIXME: what if there are multiple blocks with the same expected payoff?
    max_expected_payoff = max(expected_payoffs, key=itemgetter(1))
    t = max_expected_payoff[0]

    #p = max_expected_payoff[1]
    #print(p)



    return t









#CLASSES //////////////////////////////////////////////////////////////////////////////////////////////////////

class Block:
    def __init__(self, _h, _p, _i):
        self.genesis = False
        self.height = _h #the period 't' where the block was mined.
        self.parent = _p #height of parent block
        self.iota = _i

    def printBlock(self):
        print("block", self.height, "mined by miner", f"{self.iota},", "parent is block", self.parent)



class Miner:
    def __init__(self, _T, _i):
        self.number = _i
        self.conservative = False
        self.longestchain = False
        self.naive = False
        self.winner = np.full(_T, False) #keeps track of the stages 't' where this miner won, the value of 'winner[t]' is 'True' in that case


    def printMiner(self):
        if self.conservative:
            strategy = "conservative"
        if self.longestchain:
            strategy = "longestchain"
        if self.naive:
            strategy = "naive"

        rounds_won = np.arange(self.winner.shape[0])[self.winner]
        rounds_won = rounds_won + 1

        print("miner", self.number, f"({strategy}),", "wins rounds", rounds_won)



class Blockchain:
    def __init__(self, _T, _n, _p, _q, _r):
        #
        #'_T' is the time horizon
        #'_n' is the number of miners
        #'_p' is the number of conservative miners, '_q' is the number of longest-chain miners, '_r' is the number of naive miners.
        #
        #self.sequence is an array with objects of class 'Block'
        #self.horizon is the time horizon of the game
        #self.miners is an array filled with objects of class 'Miner'
        #self.winners is an array of with the indices of the miners that won in each round
        #
        assert _n == _p + _q + _r, "Total number of miners must equal the sum of all miner types: n must equal p + q + r"

        self.horizon = _T
        self.sequence = np.array([])

        #NOTE: self.sequence = np.full(_T+1, Block(np.nan, np.nan, np.nan)) does not work, because then all blocks in the array refer to the same Block object.
        #we have to fill it one-by-one with separate Block objects
        for i in range(_T+1):  #fill a chain with default Blocks, we have 'T+1' blocks: that is 'T' blocks mined plus the genesis block
            self.sequence = np.append(self.sequence, Block(np.nan, np.nan, np.nan))

        self.sequence[0].height = 0 #define genesis block
        self.sequence[0].genesis = True
        self.sequence[0].parent = 0


        self.miners = self.__assignMiners(_n, _p, _q, _r)
        self.winners = self.__drawWinners()

        self.__generateChain()



    def __assignMiners(self, _n, _p, _q, _r):
        #
        #assign miners and their strategies
        #

        T = self.horizon

        miners = np.array([])
        for i in range(_n):
            miners = np.append(miners, Miner(T, np.nan))

        for i in range(_p):
            miners[i].number = i
            miners[i].conservative = True

        for i in range(_p, _p + _q):
            miners[i].number = i
            miners[i].longestchain = True

        for i in range(_p + _q, _n):
            miners[i].number = i
            miners[i].naive = True

        return miners



    def __drawWinners(self):
        #
        #draws a winner for each stage 't' in {0, ..., T}
        #updates the miner attribute accordingly
        #and returns an array with the indices of the miners that won in each round
        #
        T = self.horizon
        n = self.miners.shape[0]

        winners = np.random.randint(0, n, T) #winners at each stage, 'Winners[t]' is the index of the winning miner at stage 't'

        for miner in self.miners: #for each miner
            for t in range(winners.shape[0]): #for each stage 't'
                if miner.number == winners[t]:
                    miner.winner[t] = True

        return winners



    def __generateChain(self):
        #
        #generates the chain according to the miners strategies and the rounds they win
        #NOTE: for now we ignore the strategies and just draw random blocks to mine at for each miner
        #
        T = self.horizon
        n = self.miners.shape[0]

        S = np.full((n, T), 0)

        for t in range(1, T):
            for i in range(n):
                S[i, t] = np.random.randint(0, t+1, 1) #strategies for each player in each stage, blocks are randomly chosen


        for t in range(1, T+1): #for each element in the blockchain
            self.sequence[t].height = t
            self.sequence[t].parent = S[self.winners[t-1], t-1] #the parent of the block in 't' is the strategy of the winner of stage 't-1'
            self.sequence[t].iota = self.winners[t-1]



    def copyAndExtend(self, _i, _t):
        #
        #returns an extended copy of the base chain, extended by one block, which is appended at block at height '_t'
        #miner '_i' wins the appended block
        #

        #FIXME: this is very inefficient, but it works. it should be optimized at a later time.
        #NOTE: you could try and create a method 'extendBlockchain()' that simply adds one block. problem: extending arrays is inefficient.


        T = self.horizon
        n = self.miners.shape[0]
        p, q, r = 0, 0, 0
        for miner in self.miners:
            if miner.conservative == True:
                p += 1
            if miner.longestchain == True:
                q += 1
            if miner.naive == True:
                r += 1

        B_ext = Blockchain(T+1, n, p, q, r) #create a new blockchain

        #update miners
        for i in range(n):
            B_ext.miners[i].number = self.miners[i].number
            B_ext.miners[i].conservative = self.miners[i].conservative
            B_ext.miners[i].longestchain = self.miners[i].longestchain
            B_ext.miners[i].naive = self.miners[i].naive
            B_ext.miners[i].winner = self.miners[i].winner
            if i == _i:
                B_ext.miners[i].winner = np.append(B_ext.miners[i].winner, True)
            else:
                B_ext.miners[i].winner = np.append(B_ext.miners[i].winner, False)


        B_ext.winners = np.append(self.winners, _i) #copy winners


        #copy existing chain
        for t in range(T+1):
            B_ext.sequence[t] = self.sequence[t]

        #update last block
        B_ext.sequence[-1].height = T+1
        B_ext.sequence[-1].parent = _t
        B_ext.sequence[-1].iota = _i


        from treelib import Tree
        import graphviz

        """
        ### PRINTS FOR DEBUGGING ###
        print("the extended blockchain looks like this:")
        tree = Tree()
        G = B_ext.horizon
        for t in range(G+1):
            if t == 0:
                tree.create_node(f"b{B_ext.sequence[0].height}", f"{B_ext.sequence[0].height}")
            else:
                tree.create_node(f"b{B_ext.sequence[t].height}", f"{B_ext.sequence[t].height}", parent=f"{B_ext.sequence[t].parent}")
        print("")
        tree.show()
        first = False

        for i in range(n):
            print("base")
            self.miners[i].printMiner()
            print("extended")
            B_ext.miners[i].printMiner()
        """

        return B_ext




    def getOriginalChain(self, _t): #will be used for conservative mining strategy
        #
        #'_t' is the stage at which the original chain should be calculated
        #returns a list with the stages where the blocks of the original chain were mined
        #example: if the original chain is {b0, b1, b2, b4} it returns a list [0, 1, 2, 4]
        #

        chain = [0]

        jump = 0
        last = False
        for t in range(_t+1): #for each block
            if last:
                break
            if jump > 0:
                jump -= 1
                continue
            for s in range(t+1, _t+1): #for each possible child of block 't'
                if self.sequence[s].parent == t: #find the block with the lowest index, that has the block at 't' as a parent
                    chain.append(s)
                    jump = s - t -1
                    childless = True

                    for u in range(s+1, _t+1):
                        if self.sequence[u].parent == s: #if there are no blocks that refer to block 's' as their parent (i.e. childless == True), then block 's' is the last one in the original chain
                            childless = False
                            break

                    if childless == True:
                        last = True
                    break

        return chain



    def getLongestChains(self, _t): #will be used for longest-chain mining strategy
        #
        #'_t' is the stage at which the longest chain should be calculated
        #returns a list of lists filled with the stages where the blocks of the longest chains were mined
        #example: if the longest chain is {b0, b1, b2, b4, b6, b9} it returns a list [[0, 1, 2, 4, 6, 9]]
        #

        longest_chains = []
        longest_chain_length = 0

        for t in range(_t+1): #for each block
            #test if the block 't' has a child, if not, then it is the last block in a chain
            #we take advantage of the fact that chains that end at blocks with a child can never be the longest
            childless = True

            for s in range(t+1, _t+1): #for each possible child of block 't'
                if self.sequence[s].parent == t: #if block 't' has a child
                    childless = False
                    break

            if childless == True: #if block 't' is childless
                candidate_chain = [0]
                u = t
                while self.sequence[u].genesis != True:
                    candidate_chain.append(u)
                    u = self.sequence[u].parent
                if len(candidate_chain) >= longest_chain_length:
                    candidate_chain.sort()
                    if len(candidate_chain) == longest_chain_length:
                        longest_chains.append(candidate_chain)
                    if len(candidate_chain) > longest_chain_length:
                        longest_chain_length = len(candidate_chain)
                        longest_chains = [candidate_chain]


        return longest_chains



    def getPayoff(self, _i, _t):
        #
        #sums up all the blocks miner $_i$ mined in the chain going from block 0 to block $_t$
        #returns an integer corresponding to the payoff if the game were to end in '_t'
        #

        payoff = 0

        t = _t

        while self.sequence[t].genesis != True:
            if self.winners[t-1] == _i:
                payoff += 1
            t = self.sequence[t].parent

        return payoff



    def getConservativeStrategy(self, _t):
        #
        #returns the block where conservative miners mine at
        #'_t' is the stage at which we want to compute the strategy
        #

        chain = self.getOriginalChain(_t)

        return chain[-1]



    def getLongestChainStrategy(self, _i, _t):
        #
        #returns the block where a longest chain miner mines at
        #'_i' is the index of the miner we want to compute the strategy for
        #'_t' is the stage at which we want to compute the strategy
        #

        chains = self.getLongestChains(_t)

        #we must consider past won blocks
        if len(chains) == 1: #if there is only one longest chain, the miner chooses that one
            return chains[0][-1]
        else: #if there are multiple longest chains
            p = np.array([]) #use numpy because of useful methods for this problem
            for chain in chains:
                p = np.append(p, self.getPayoff(_i, chain[-1]))
            largest = np.where(p == np.max(p)) #returns np.array of indices of the longest chains within 'chains' with the largest payoff for miner '_i'
            if largest[0].shape[0] == 1: #if there is one chain with larger payoff than all other longest chains, the miner chooses that one
                return chains[largest[0][0]][-1]
            else: #if there are multiple longest chains with the same largest payoff, the miner chooses one at random
                r = np.random.randint(0, largest[0].shape[0])
                return chains[r][-1]



    def chainLength(self, _t):
        #
        #this function is self explanatory
        #

        #calculate length of the chain ending in block '_t'
        length = 1 #we must start at 1 because the genesis block is not counted in the while loop below

        t = _t

        while self.sequence[t].genesis != True:
            length += 1
            t = self.sequence[t].parent

        return length



    def willBeLongestChain(self, _t):
        #
        #takes the height '_t' of a block as an argument
        #checks if the chain resulting when a block is appended to 'b_t' is one of the longest chains in the next stage
        #returns True or False, along with the number of longest chains 'l'
        #

        T = self.horizon
        chains = self.getLongestChains(T)
        l = len(chains)
        length_longest = len(chains[0]) #length of longest chain(s) now
        length_future = self.chainLength(_t) + 1 #length of the chain if a block is appended to 'b_t'

        if length_future == length_longest:
            return True, l+1
        if length_future > length_longest:
            return True, 1
        if length_future < length_longest:
            return False, l




    def getNaiveStrategy(self, _i, _t):
        #
        #returns the block where a naive miner mines at
        #'_i' is the index of the miner we want to compute the strategy for
        #'_t' is the stage at which we want to compute the strategy
        #
        #simply calls 'getDecisionRelevantPayoff' repeatedly and selects the block with the highest payoff.

        p = np.array([]) #use numpy because of useful methods for this problem

        for t in range(_t+1):
            p = np.append(p, self.getDecisionRelevantPayoff(_i, t))


        largest = np.where(p == np.max(p)) #returns np.array of indices of the longest chains within 'chains' with the largest payoff for miner '_i'
        if largest[0].shape[0] == 1: #if there is one chain with larger payoff than all other longest chains, the miner chooses that one
            return largest[0][0]
        else: #if there are multiple longest chains with the same largest payoff, the miner chooses one at random
            r = np.random.randint(0, largest[0].shape[0])
            return largest[0][r]



    def getDecisionRelevantPayoff(self, _i, _t): #will be used for naive mining strategy
        #
        #returns the decision-relevant payoff for miner '_i' if he mines at block '_t', under the assumption that the game ends after this round.
        #
        #NOTE: if the naive miner does NOT win the round, their decision of where to append the block is irrelevant.
        #the block they choose does not influence their payoff when they lose, hence they must be indifferent between all blocks if that is the case.
        #we therefore only have to consider the payoff in the case where the naive miner wins. this is what we call the 'decision-relevant' payoff.
        #the decision-relevant payoff has the property, that the naive miner always prefers to mine at blocks which have a higher decision-relevant payoff
        #[this statement is intuitive, but a formal proof will be in the written thesis]
        #
        #the decision-relevant payoff is equal to whatever the payoff of the resulting situation (under the assumption the naive miner wins) is.
        #the factor (1/n) is actually not necessary. since all payoffs are multiplied by it, it can be ignored without changing the order of preference for the blocks.
        #
        #why do it like this? it is a shortcut. calculating the entire payoff is hard, convoluted (and unnecessary if the statement above holds)
        #
        #   *the complexity stems from the fact that we do not know where the next block will be appended.*
        #
        #NOTE: if the resulting chain is not one of the longest chains, it is irrelevant for the calculation and can be ignored.
        #if it is not one of the longest chains, then mining at that block is always weakly dominated by mining at the longest chain.
        #why? because the naive miner cannot gain anything from appending a block there. even if they win, they don't get the reward because there is a longer chain elsewhere.
        #the naive miner therefore always prefers mining on a longest chain compared to mining at a block that does not result in a longest chain if they win.


        v = 0
        T = self.horizon
        n = self.miners.shape[0]
        chains = self.getLongestChains(T)

        #check if a block appended at 'b_t' leads to a chain that is one of the longest chains, or the longest
        #if not, then appending at this block can never be optimal; this block is skipped.
        willBeLongest, l = self.willBeLongestChain(_t)
        if willBeLongest == True:
            #if yes, calculate the payoff in 't+1' if a block were to be appended there
            if l == 1: #check if the chain is the single longest chain
                v = 1 + self.getPayoff(_i, _t) #we operate under the assumption that the naive miner wins this stage, i.e. the expected payoff is 1 + whatever payoffs we get from past blocks in the chain
            else:
                #if not, then compute the expected value 'v' if each chain is chosen with equal probability.
                v_star = 1 + self.getPayoff(_i, _t)
                temp_sum = 0
                for i in range(len(chains)):
                    temp_sum += self.getPayoff(_i, chains[i][-1]) #sum all the payoffs of all the other longest chains
                v = (1/l) * (v_star + temp_sum)

        return v



