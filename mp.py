import numpy as np
from scipy import sparse



class MatchingPursuit:
    """ Define the matching puirsuit algorithm """
    
    
    def __init__(self,dictionary,m):
        """ __init__:
            mdct -> mdct object which define the dictionary
            m -> number of atoms in the sparse decomposition
        """
        self.dictionary = dictionary;
        self.m = m;



    def sparse(self,s):
        """ sparse:
            s -> the signal to be decomposed
        """
        # Residual
        res = s;
        # Size of the sparse decompositon
        nd = s.size*self.dictionary.sizes.size
        # Decomposed signal
        y = sparse.lil_matrix((1,nd))

        # Loop until we got m atoms
        while y.getnnz() < self.m:
            tmp = self.dictionary.mdctOp(res)
            #Select new element
            new = np.argmax(abs(tmp))
            # update coefficient
            y[0,new] += tmp[new]
            tmp[np.arange(nd)!=new] = 0
            res -=  self.dictionary.imdctOp(tmp)
        
        return y.todense().A1
