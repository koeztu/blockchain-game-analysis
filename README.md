# blockchain-game-analysis

We can now calculate the optimal strategy in period 't' for any miner for any (randomly generated) base blockchain with horizon 'T' looking any number of periods 'tt = TT - T' into the future (where 'TT' is the horizon of the extended blockchain).

It is also possible to specify a base chain 'by-hand'.

Some performance improvements have been made too. But the combinatorial explosion really does slow things down. On my machine it usually takes around 1 second to calculate the optimal strategy for a miner on a base chain of length 10 (exluding genesis block), an extended horizon of 5 periods, and 3 miners. The time it takes also depend on the number of blocks without a child, since the recursion function is called at each one of those.


### IMPORTANT NOTICE 
It is possible that running the code on a huge blockchain with an extremely long time-horizon 'TT' for the extended blockchain could cause your computer to run out of memory. The code makes use of recursion and there is no limit on how much ram it could potentially eat up. I have not tested this and there are no safeties in place to prevent your computer from seizing up. Be warned :)


---
Please read in-file comments for further explanations.

Files last updated on Feb. 13
