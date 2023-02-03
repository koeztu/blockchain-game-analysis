import numpy as np



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




    #TODO: the following two functions

    def getNaiveStrategy(self, _i, _t):
        #
        #returns the block where a naive miner mines at
        #'_i' is the index of the miner we want to compute the strategy for
        #'_t' is the stage at which we want to compute the strategy
        #
        #simply calls 'getNaiveExpectedPayoff' repeatedly and selects the block with the highest payoff.

        p = np.array([]) #use numpy because of useful methods for this problem

        for t in range(_t+1):
            p = np.append(p, self.getNaiveDecisionRelevantPayoff(_i, t))


        largest = np.where(p == np.max(p)) #returns np.array of indices of the longest chains within 'chains' with the largest payoff for miner '_i'
        if largest[0].shape[0] == 1: #if there is one chain with larger payoff than all other longest chains, the miner chooses that one
            return largest[0][0]
        else: #if there are multiple longest chains with the same largest payoff, the miner chooses one at random
            r = np.random.randint(0, largest[0].shape[0])
            return largest[0][r]



    def getNaiveDecisionRelevantPayoff(self, _i, _t): #will be used for naive mining strategy
        #
        #returns the expected payoff for miner '_m' if he mines at block '_t', under the assumption that the game ends after this round.
        #
        #NOTE: if the naive miner does NOT win the round, their decision of where to append the block is irrelevant.
        #the block they choose does not influence their payoff when they lose, hence they must be indifferent between all blocks if that is the case.
        #we therefore only have to consider the payoff in the case where the naive miner wins. this is what we call the 'decision-relevant' payoff.
        #the decision-relevant payoff has the property, that the naive miner always prefers to mine at blocks which have a higher decision-relevant payoff
        #[this statement is intuitive (but could be false!), a formal proof is necessary]
        #
        #the decision-relevant payoff is (1/n) * whatever the payoff of the resulting situation (under the assumption the naive miner wins) is.
        #
        #why do it like this? it is a shortcut. calculating the entire payoff is hard, convoluted, and unnecessary (if the statement above holds)
        #
        #   *the complexity stems from the fact that we do not know where the next block will be appended.*
        #
        #NOTE: if the resulting chain is not one of the longest chains, it is irrelevant for the payoff calculation.
        #if it is not one of the longest chains, then mining at that block is always weakly dominated by mining at the longest chain.
        #why? because the naive miner cannot gain anything from appending a block there. even if they win, they don't get the reward because there is a longer chain elsewhere.
        #[formal proof pending]


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


        return (1/n) * v #the naive miner gets the calculated payoff only if they win, i.e. with probability (1/n)



    #TODO: method for calculating expected payoff in t=T for any miner and all types (HARD)
    #TODO: method that returns the optimal block to mine at for a miner at any stage (HARD)
    #TODO: this function may be useful in the future: calculate the probability alpha0, alpha1, ... that a block will be appended to a given block 0, 1, ... in the next round
