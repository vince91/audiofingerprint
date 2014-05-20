import scipy.io.wavfile as wv
from numpy import *
from mdct import *
from mp import *
from time import time


(Fe,s) = wv.read('glockenspiel.wav')
s=s[:12*8192]
s=float64(s)

d = Mdct()
mp = MatchingPursuit(d,100)

#y =mp.sparse(s)
y = mp.sparse(s)
x = d.imdctOp(y)
end = time()
wv.write('result.wav',Fe,int16(s))
