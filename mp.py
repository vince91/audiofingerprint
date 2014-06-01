import numpy as np
from hashlib import sha1



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
        res = np.copy(s)
        N = np.size(s)
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
            print(i, " ", new)
            tmp = self.dictionary.mdctOp(res,update=new,old=tmp)
            #Select new element
            i+=1
            new = np.argmax(abs(tmp)*(1-mask))
            #udpate mask
            atom = self.dictionary.atom(N,new)
            if y[new] == 0:
                maskupdate = np.zeros(nd)
                self.dictionary.mdctOp(atom,update=new,old=maskupdate)
                mask = np.maximum(mask,maskupdate)
            # update coefficient
            y[new] += tmp[new]
            res -=  tmp[new] * atom
        
        return y

    def extractAtoms(self, y):
        indices = np.nonzero(y)[0]
        signal_size = y.size/self.dictionary.sizes.size

        key_list = []

        for i in indices:
            atom_size_index = i//signal_size
            atom_size = self.dictionary.sizes[atom_size_index]
            signal_index = i%signal_size
            frequency_index = signal_index%(atom_size//2)
            offset = int(2*signal_index/atom_size)*atom_size/2
            key_list.append((atom_size, frequency_index, offset))

        return key_list

    def extractKeys(self, y):
        
        entries = []
        atoms = self.extractAtoms(y)
        for i in range(len(atoms) - 1):
            for j in range(i+1,len(atoms)):
                offseti = int(atoms[i][2])
                offsetj = int(atoms[j][2])
                stringi = (str(atoms[i][0])) + '-' + str(atoms[i][1])
                stringj = (str(atoms[j][0])) + '-' + str(atoms[j][1])
                string = (stringi+','+stringj+','+str(offseti - offsetj)).encode('utf-8')
                key_hash = sha1(string).digest()
                entries.append((key_hash, offseti)) 

        return entries
                
