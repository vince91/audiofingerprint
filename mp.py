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
        y = np.zeros(nd)
        # Mask
        mask = np.zeros(nd)
        i=0
        
        new = None
        tmp = None
        # Loop until we got m atoms
        while np.count_nonzero(y) <=  self.m:
            print('\n',i, " ", new)
            tmp = self.dictionary.mdctOp(res,update=new,old=tmp)
            #Select new element
            i+=1
            new = np.argmax(abs(tmp)*(1-mask))
            #udpate mask
            if y[new] == 0:
                tmp2 = np.zeros(nd)
                tmp2[new] = 1;
                tmp2 = self.dictionary.imdctOp(tmp2)
                mask = np.maximum(mask,self.dictionary.mdctOp(tmp2))
            # update coefficient
            y[new] += tmp[new]
            tmp[np.arange(nd)!=new] = 0
            res -=  self.dictionary.imdctOp(tmp)
        
        return y
