import numpy as np


#CLASSES ///////////////////////////////////////////////////////////////////////////////

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


"""
    def getNaiveExpectedPayoff(self, _t, _m): #will be used for naive mining strategy
        #
        #returns the expected payoff for miner '_m' if he mines at block '_t', under the assumption that the game ends after this round.
        #

        for t in range(_t+1):
            payoff = 0
            while self.sequence[u].genesis != True:
                if self.winners[u] == _m: #if miner '_m' won block 'u'
                    payoff += 1
                u = self.sequence[u].parent
            payoff_win = (payoff + 1) / len(self.miners) #expected payoff when winning the next round, the chance to win is 1/n

        #FIXME: this is a hard problem that will take a while to solve!


        return 0
"""

    #TODO: method for calculating expected payoff in t=T (HARD)
    #TODO: method that returns the block a miner would want to mine at according to his strategy
    #TODO: method that returns the optimal block to mine at for a miner at any stage
