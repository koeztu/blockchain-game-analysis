import numpy as np
from operator import itemgetter
import csv


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
        self.number = _i #FIXME: this is confusingly named, the number really is the index!
        self.winner = np.full(_T, False) #keeps track of the stages 't' where this miner won, the value of 'winner[t]' is 'True' in that case


    def printMiner(self):

        stages_won = np.arange(self.winner.shape[0])[self.winner]
        stages_won = stages_won + 1

        print("miner", self.number, "wins stages", stages_won)



class Blockchain:
    def __init__(self, _n, _parents, _winners):
        #
        #'_types' is an np.array where types[0] is the number of conservative miners, types[1] is the number of longest-chain miners, and types[2] is the number of naive miners
        #'_parents' is an np.array where _structure[t] is the parent of block 't+1', e.g. the fifth element is the index of the parent of the block in t=5
        #'_winners' is an np.array where _winners[t] is the index of the winner of stage 't+1'
        #
        #self.sequence is an array with objects of class 'Block'
        #self.horizon is the time horizon of the game
        #self.miners is an array filled with objects of class 'Miner'
        #self.winners is an array of with the indices of the miners that won in each round
        #

        self.n = _n
        self.parents = _parents
        self.winners = _winners
        self.horizon = self.parents.shape[0]

        self.miners = self.__assignMiners()
        self.sequence = self.__generateChain()

        #pre-calculate longest chains for more speed
        #we only ever need to know the longest chain at the end of the game, not at intermediate steps. we take advantage of this fact.
        self.longestchains = self.__getLongestChains() #a list of lists



    def __assignMiners(self):
        #
        #assign miners and their strategies
        #

        miners = np.array([])
        for i in range(self.n):
            miners = np.append(miners, Miner(self.horizon, i))

        #assign winners
        for miner in miners: #for each miner
            for t in range(self.winners.shape[0]): #for each stage 't'
                if miner.number == self.winners[t]:
                    miner.winner[t] = True

        return miners



    def __generateChain(self):
        #
        #generates the chain according to the miners strategies and the rounds they win
        #NOTE: for now we ignore the strategies and just draw random blocks to mine at for each miner
        #

        #NOTE: self.sequence = np.full(_T+1, Block(np.nan, np.nan, np.nan)) does not work, because then all blocks in the array refer to the same Block object.
        #we have to fill it one-by-one with separate Block objects
        sequence = [] #use list because appending to lists is 5x faster than appending to numpy arrays
        for t in range(self.horizon + 1):  #fill a chain with default Blocks, we have 'T+1' blocks: that is 'T' blocks mined plus the genesis block
            if t == 0:
                sequence.append(Block(0, np.nan, np.nan))
                sequence[0].genesis = True
            else:
                sequence.append(Block(t,
                                      self.parents[t-1],
                                      self.winners[t-1]))

        sequence = np.array(sequence) #convert to numpy array
        return sequence



    def __getLongestChains(self): #will be used for longest-chain mining strategy
        #
        #'_t' is the stage at which the longest chain should be calculated
        #returns a list of lists filled with the stages where the blocks of the longest chains were mined
        #example: if the longest chain is {b0, b1, b2, b4, b6, b9} it returns a list [[0, 1, 2, 4, 6, 9]]
        #

        T = self.horizon
        longest_chains = []
        longest_chain_length = 0

        for t in range(T+1): #for each block
            #test if the block 't' has a child, if not, then it is the last block in a chain
            #we take advantage of the fact that chains that end at blocks with a child can never be the longest
            childless = True

            for s in range(t+1, T+1): #for each possible child of block 't'
                if self.sequence[s].parent == t: #if block 't' has a child
                    childless = False
                    break

            if childless == True: #if block 't' is childless
                candidate_chain = [0]
                u = t
                while self.sequence[u].genesis != True:
                    candidate_chain.append(u)
                    u = self.sequence[u].parent
                length_candidate_chain = len(candidate_chain)
                if length_candidate_chain >= longest_chain_length:
                    candidate_chain.sort()
                    if length_candidate_chain == longest_chain_length:
                        longest_chains.append(candidate_chain)
                    if length_candidate_chain > longest_chain_length:
                        longest_chain_length = length_candidate_chain
                        longest_chains = [candidate_chain]


        return longest_chains


    def to_csv(self, _filename):
        #
        #print the chain into a csv file, that is
        #   a sequence of blocks
        #   the parent of each block
        #   the miner who mined the block
        #
        #this will be used to save the counterexamples, if there are any.
        #

        file = open(_filename, 'w')
        writer = csv.writer(file)

        row = ["block"]
        for t in range(self.horizon):
            row.append(t+1)
        writer.writerow(row) #write one row

        row = ["parent"]
        for t in range(self.horizon):
            row.append(self.parents[t])
        writer.writerow(row) #write one row

        row = ["winner"]
        for t in range(self.horizon):
            row.append(self.winners[t])
        writer.writerow(row) #write one row

        file.close()



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



    def getConservativeStrategy(self):
        #
        #returns the block where conservative miners mine at
        #'_t' is the stage at which we want to compute the strategy
        #

        chain = self.getOriginalChain(self.horizon)

        return [chain[-1]]


    def getLongestChainStrategies(self, _i):
        #
        #returns a list of blocks where a longest chain miner mines at
        #'_i' is the index of the miner we want to compute the strategy for
        #we compute the strategy for the current blockchain
        #

        chains = self.longestchains

        #we must consider past won blocks
        if len(chains) == 1: #if there is only one longest chain, the miner chooses that one
            return [chains[0][-1]]
        else: #if there are multiple longest chains
            p = np.array([]) #use numpy because of useful methods for this problem
            for chain in chains:
                p = np.append(p, self.getPayoff(_i, chain[-1]))
            largest = np.where(p == np.max(p)) #returns np.array of indices of the longest chains within 'chains' with the largest payoff for miner '_i'
            if largest[0].shape[0] == 1: #if there is one chain with larger payoff than all other longest chains, the miner chooses that one
                return [chains[largest[0][0]][-1]]
            else: #if there are multiple longest chains with the same largest payoff, the miner chooses one at random
                blocks = []
                for i in range(largest[0].shape[0]):
                    blocks.append(chains[largest[0][i]][-1])
                return blocks



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
        chains = self.longestchains
        l = len(chains)
        length_longest = len(chains[0]) #length of longest chain(s) now
        length_future = self.chainLength(_t) + 1 #length of the chain if a block is appended to 'b_t'

        if length_future == length_longest:
            return True, l+1
        if length_future > length_longest:
            return True, 1
        if length_future < length_longest:
            return False, l




    def getNaiveStrategies(self, _i, _t):
        #
        #returns a list with blocks where a naive miner would want to mine at
        #'_i' is the index of the miner we want to compute the strategy for
        #'_t' is the stage at which we want to compute the strategy
        #
        #simply calls 'getDecisionRelevantPayoff' repeatedly and selects the block with the highest payoff.

        p = [] #list of decision-relevant payoffs
        blocks = [] #list of blocks
        for t in range(_t+1):
            p.append(self.getDecisionRelevantPayoff(_i, t))

        largest = np.where(p == np.max(p)) #returns np.array of indices of the longest chains within 'chains' with the largest payoff for miner '_i'
        if largest[0].shape[0] == 1: #if there is one chain with larger payoff than all other longest chains, the miner chooses that one
            blocks.append(largest[0][0])
        else: #if there are multiple longest chains with the same largest payoff
            for i in range(largest[0].shape[0]):
                blocks.append(largest[0][i])

        return blocks




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
        chains = self.longestchains

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



class ExtendedBlockchain(Blockchain):
    def __init__(self, _B, _i, _t):
        #
        #an extended copy of the base blockchain '_B', extended by one block, which is appended at block at height '_t'
        #miner '_i' wins the appended block
        #
        #NOTE: this class replaces the function 'copyAndExtend' from previous versions of the code

        n = _B.n
        parents = np.append(_B.parents, _t) #extend
        winners = np.append(_B.winners, _i) #extend

        Blockchain.__init__(self, n, parents, winners) #build


class ShortenedBlockchain(Blockchain):
    def __init__(self, _B):
        #
        #a shortened copy of the base blockchain '_B'
        #the most recent block is removed
        #

        n = _B.n
        parents = _B.parents[:-1] #shorten
        winners = _B.winners[:-1] #shorten

        Blockchain.__init__(self, n, parents, winners) #build

