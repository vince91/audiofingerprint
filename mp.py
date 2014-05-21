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
        res = np.copy(s);
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

    def extractKey(self, y):
        indices = np.nonzero(y)[0]
        signal_size = y.size/self.dictionary.sizes.size

        key_list = []

        for i in indices:
            atom_size_index = i//signal_size
            atom_size = self.dictionary.sizes[atom_size_index]
            signal_index = i%signal_size
            frequency_index = signal_index%atom_size
            time_index = signal_index//atom_size
            key_list.append((atom_size, frequency_index, time_index))

        return key_list
