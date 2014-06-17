import numpy as np
from hashlib import sha1
from db import Database



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


        for k in range(4):
            # Mask
            mask = np.int16(np.zeros(nd))
           
            
            for i in range(self.dictionary.sizes.size):
                K = int(self.dictionary.sizes[i]/2)
                for j in range(int(N/K)):
                    mask[i*N + (j+k/4)*K: i*N+(j+(k+1)/4)*K] = np.ones(K/4) 
           
           
            i=0
            new = None
            tmp = None
            # Loop until we got m atoms
            for i in range(self.m//4):
                #print(i, "\t", new)
                tmp = self.dictionary.mdctOp(res,update=new,old=tmp)
                #Select new element
                i+=1
                new = np.argmax(abs(tmp * mask))
                #udpate mask
                if y[new] == 0:
                    # index of size
                    nid = new//N
                    # size of new
                    nsize = self.dictionary.sizes[nid]
                    # frame index of the new item
                    nframe = (new%N)//(nsize//2)
                    # time of the atom
                    ntime = nframe*(nsize//2)
                    # freq of the new atom
                    nfreq = (new%N)%(nsize//2)

                    for j in range(self.dictionary.sizes.size):
                        size = self.dictionary.sizes[j]
                        K=size//2
                        first = ntime//K
                        first = first - 1 if first > 0 else 0
                        last = np.minimum( (ntime+nsize-1) // K + 1, N//K)
                        freq = int(nfreq/nsize*size)
                        deltafreq = int(0.03*size - 1/2)
                        for frame in range(first,last):
                            mask[j*N+frame*K+freq - deltafreq:j*N+frame*K +freq +deltafreq] = 0

                # update coefficient
                y[new] += tmp[new]
                atom = self.dictionary.atom(N,new)
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
            k=0
            asize,freq,offset = atoms[i]
            for j in range(i+1,len(atoms)):
                asizej,freqj,offsetj = atoms[j]
                deltat = int(offsetj - offset)
                if abs(deltat) <= 6.5*8192 and np.abs((freqj+1/2)/asizej - (freq+1/2)/asize) <= 0.18:
                    stringi = (str(asize)) + '-' + str(freq)
                    stringj = (str(asizej)) + '-' + str(freqj)
                    string = (stringi+','+stringj+','+str(int(deltat))).encode('utf-8')
                    key_hash = sha1(string).digest()
                    entries.append((key_hash, int(offset)))

        return entries
                


    def match(self,s):

        y = self.sparse(s)
        # keys for the signal
        keys = self.extractKeys(y)
        db = Database()
        
        offsets = {}
        # Quantiztion factor for the offsets
        qt = max(self.dictionary.sizes)/2
        for hash_key,offset in keys:
            result = db.selectFingerprints(hash_key)
            for r in result:
                if not r[0] in offsets:
                    offsets[r[0]] = []
                offsets[r[0]].append((r[1] - offset)//qt * qt)

        songid = None
        max_offset = 0
        # proceed the histogram
        for song,o in offsets.items():
            # extract the most common offset
            tmp_max = o.count(max(set(o), key=o.count))
            if tmp_max > max_offset:
                max_offset = tmp_max
                songid = song

        return songid,offsets


