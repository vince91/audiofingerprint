from numpy import *


class  MdctDictionary: 
    """ Define the MDCT dictionary class used for Sparse decomposition """
    

    def __init__(self,sizes=array([128,1024,8192]),window=lambda x: sin(pi*(x+1/2)/x.size) ):
        """ __init__:
            size (array) -> define the sizes of mdct atoms
            window (lambda fun) -> define the function used to window atoms
        """        
        self.sizes = sizes
        self.window = window

    def mdctOp(self,s):
        """ mdctOp
            s (array) -> the signal vector to be decomposed
            Output (array) -> the solution array
        """
        N = s.size
        L = self.sizes.size
        x = zeros(L*N)
        for i in range(L):
             x[i*N:(i+1)*N] = self.mdct(s, self.sizes[i])/sqrt(L)
        return x
    



    def mdct(self,s,L):
        """ mdct
            s (array) -> the signal vector to be decomposed
            L (int) -> the size of the atoms
            Output -> the solution array for this size
        """
        # TODO : check if N is a multiple of K, or else return with error
        #       define other error cases (P < 2,...)
        
        # Size of the signal
        N = s.size
        # Number of frequency channels
        K = int(L/2)
        # Number of frames
        P = int(N/K)

        # Pad egdes with zeros
        x = hstack( (zeros(K/2), s, zeros(K/2)) )

        # Framing
        fidx = K *arange(P)
        fidx = tile(fidx,(L,1)).transpose() # tile array to dimension P*L
        sidx = arange(L)
        sidx = tile(sidx,(P,1))
        x = x[fidx+sidx]

        # Windowing
        win = self.window(arange(L))
        winL = win
        winL[0:L/4] = 0
        winL[L/4:L/2] = 1
        winR = win
        winR[L/2:3*L/4] = 1
        winR[3*L/4:] = 0
        x[0,:] *= winL
        x[1:-1,:] *= tile(win,(P-2,1))
        x[-1,:] *= winR

        # Pre-twidle
        x = complex_(x)
        x *= tile(exp(-1j*pi*arange(L)/L), (P,1) )
        
        # FFT
        y = fft.fft(x)

        # Post-twidle
        y = y[:,:L/2]
        y *= tile(exp(-1j*pi*(L/2+1)*arange(1/2,(L+1)/2)),(P,1))

        # Real part & scaling
        return sqrt(2/K)*real(y.ravel())
        




            


