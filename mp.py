import numpy as np
from hashlib import sha1
from db import Database
from sqlite3 import Binary



class MatchingPursuit:
    """ Define the matching puirsuit algorithm """
    
    
    def __init__(self,dictionary,m):
        """ __init__:
            mdct -> mdct object which define the dictionary
            m -> number of atoms in the sparse decomposition
        """
        self.dictionary = dictionary;
        self.m = m;
        self.mask = None
        self.__initMask()


    def __initMask(self):
        """ __initMask
            init the Mask pattern for each size
        """

        self.maskpat = {}
  
        for size in self.dictionary.sizes:
            K = int(size/2)
            self.maskpat[size] = np.ones(K)
            self.maskpat[size][:3*K/64] = np.zeros(3*K/64) 
            self.maskpat[size][7.*K/8:K] = np.zeros(K/8) 

    def getMask(self,N):
        """ getMask
            create a new mask for the given size of signal
        """

        nd = N*self.dictionary.sizes.size

        if self.mask != None and self.mask.size == nd:
            return np.copy(self.mask)
        else:
            mask = np.zeros(nd)
            i=0
            for size,m in self.maskpat.items(): 
                K=size/2
                P = int(N/K)
                mask[i*N:(i+1)*N] = np.tile(m,P)
                i +=1
            return mask

    def buildMask(self,N):
        """ buildMask
            build the mask for a given size
        """

        self.mask = self.getMask(N)


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
        mask = self.getMask(N)
       
       
        new = None
        tmp = None
        # Loop until we got m atoms
        for i in range(self.m):
            tmp = self.dictionary.mdctOp(res,update=new,old=tmp)
            #Select new element
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
        for i in range(len(atoms)):
            asize,freq,offset = atoms[i]
            pairs = [(psize,pfreq,poffset) for (psize,pfreq,poffset) in atoms if (poffset >= offset and (psize,pfreq,poffset) != (asize,freq,offset))]
                
            # cantor couple function
            def cant(k):
                    ats,fq,of = k
                    x = int(abs(800*((fq+1/2)/ats - (freq+1/2)/ats)))
                    y = int((of-offset)/500)
                    return (x+y)*(x+y+1)/2+y

            pairs.sort(key=cant)
            for j in range(min(3,len(pairs))):
                asizej,freqj,offsetj = pairs[j]
                deltat = int(offsetj - offset)
                stringi = (str(asize)) + '-' + str(freq)
                stringj = (str(asizej)) + '-' + str(freqj)
                string = (stringi+','+stringj+','+str(int(deltat))).encode('utf-8')
                key_hash = sha1(string).digest()
                entries.append((key_hash, int(offset)))

        return entries
                


    def match(self,s,db,soffset=0,offsets={}):

        y = self.sparse(s)
        # keys for the signal
        keys = self.extractKeys(y)
        
        # Quantiztion factor for the offsets
        qt = max(self.dictionary.sizes)
        for hash_key,offset in keys:
            result = db.selectFingerprints(Binary(hash_key)[0:5])
            for r in result:
                if not r[0] in offsets:
                    offsets[r[0]] = []
                offsets[r[0]].append((r[1]-offset-soffset)//qt * qt)


        maxsongid = None
        max_offset = 0.
        second_max = 0.
        # proceed the histogram
        for song,o in offsets.items():
            # extract the most common offset
            tmp_max = o.count(max(set(o), key=o.count))
            if tmp_max >= max_offset:
                second_max = max_offset
                max_offset = tmp_max
                maxsongid = song
            elif tmp_max > second_max:
                second_max = tmp_max
    
        songid = None
        if max_offset > 4 and (second_max == 0 or max_offset/second_max > 1+0.6/np.log(max_offset)):
            songid = maxsongid
        return songid,offsets


