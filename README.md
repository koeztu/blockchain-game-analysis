# blockchain-game-analysis

We can now calculate the optimal strategy in period 't' for any miner for any (randomly generated) base blockchain with horizon 'T' looking any number of periods 'tt = TT - T' into the future (where 'TT' is the horizon of the extended blockchain).

**There are known issues that need to be fixed (and will be fixed soon).**


## !!! IMPORTANT NOTICE !!!
It is possible that running the code on a huge blockchain with a long time-horizon 'TT' for the extended blockchain could cause your computer to run out of memory. The code makes use of recursion and there is no limit on how much ram it could potentially eat up. I have not tested this and there are no safties in place to prevent your computer from seizing up. Be warned :D


---
Please read in-file comments for further explanations.

Files last updated on Feb. 10
