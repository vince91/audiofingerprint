import numpy as np
from scipy import sparse


class  Mdct: 
    """ Define the MDCT dictionary class used for Sparse decomposition """
    

    def __init__(self,sizes=np.array([128,1024,8192]),window=lambda x: np.sin(np.pi*(x+1/2)/x.size) ):
        """ __init__:
            size (array) -> define the sizes of mdct atoms
            window (lambda fun) -> define the function used to window atoms
        """        
        self.sizes = sizes
        self.window = window

    def mdctOp(self,s):
        """ mdctOp
            s (np.array) -> the signal vector to be decomposed
            Output (np.array) -> the solution array
        """
        N = s.size
        L = self.sizes.size
        x = np.zeros(L*N)
        for i in range(L):
             x[i*N:(i+1)*N] = self.mdct(s, self.sizes[i])/np.sqrt(L)
        return x
    



    def mdct(self,s,L):
        """ mdct
            s (np.array) -> the signal vector to be decomposed
            L (int) -> the size of the atoms
            Output -> the solution array for this size
        """
        
        # Size of the signal
        N = s.size
        # Number of frequency channels
        K = int(L/2)
        # Number of frames
        P = int(N/K)

        # Test length
        if N % K != 0:
            raise Exception("Input length must be a multiple of the half of the window size")

        if P < 2:
            raise Exception("Signal too short")

        # Pad egdes with zeros
        x = np.hstack( (np.zeros(K/2), s, np.zeros(K/2)) )

        # Framing
        fidx = K *np.arange(P)
        fidx = np.tile(fidx,(L,1)).transpose() # tile array to dimension P*L
        sidx = np.arange(L)
        sidx = np.tile(sidx,(P,1))
        x = x[fidx+sidx]

        # Windowing
        win = self.window(np.arange(L))
        winL = np.copy(win)
        winL[0:L/4] = 0
        winL[L/4:L/2] = 1
        winR = np.copy(win)
        winR[L/2:3*L/4] = 1
        winR[3*L/4:] = 0
        x[0,:] *= winL
        x[1:-1,:] *= np.tile(win,(P-2,1))
        x[-1,:] *= winR

        # Pre-twidle
        x = np.complex_(x)
        x *= np.tile(np.exp(-1j*np.pi*np.arange(L)/L), (P,1) )
        
        # FFT
        y = np.fft.fft(x)

        # Post-twidle
        y = y[:,:L/2]
        y *= np.tile(np.exp(-1j*np.pi*(L/2+1)*np.arange(1/2.,(L+1)/2.)/L),(P,1))

        # Real part & scaling
        return np.sqrt(2./K)*y.ravel().real
        
    
    def imdctOp(self,y):
        """imdctOP: inverse mdct operator
            y(np.array) -> vector to be recomposed
            Ouput -> recomposed signal
        """
        S=self.sizes.size
        N=y.size/S
        s=np.zeros(N)

        for i in range(S):
            s += self.imdct(y[i*N:(i+1)*N], self.sizes[i])
        s/=np.sqrt(S)
        return s


    def imdct(self,y,L):
        """imdct: inverse mdct
            y(np.array) -> mdct signal
            L -> frame size
        """
        # signal size
        N = y.size
        # Number of frequency channels
        K = L/2
        # Number of frames
        P = N/K

        # Reshape y
        tmp = y.reshape(P,K)
        y = np.zeros( (P,L) )
        y[:,:K] = tmp

        # Pre-twidle
        y = np.complex_(y)
        y *= np.tile(np.exp(1j*2.*np.pi*np.arange(L)*(L/2+1)/2./L), (P,1))

        # IFFT
        x = np.fft.ifft(y);

        # Post-twidle
        x *= np.tile(np.exp((1./2.)*1j*2*np.pi*(np.arange(L)+((L/2+1)/2.))/L),(P,1));

        # Windowing
        win = self.window(np.arange(L))
        winL = np.copy(win)
        winL[:L/4] = 0
        winL[L/4:L/2] = 1
        winR = np.copy(win)
        winR[L/2:3*L/4] = 1
        winR[3*L/4:] = 0
        x[0,:] *= winL
        x[1:-1,:] *= np.tile(win,(P-2,1))
        x[-1,:] *= winR

        # Real part & scaling
        x = np.sqrt(2./K)*L*x.real

        # Overlap and add
        b = np.repeat(np.arange(P),L)
        a = np.tile(np.arange(L),P) + b*K
        x = sparse.coo_matrix((x.ravel(),(b,a)),shape=(P,N+K)).sum(axis=0).A1

        # Cut edges
        return x[K/2:-K/2]




            


