import os
import numpy as np
import sound
import hashlib
from db import *
import matplotlib.pyplot as plt
from mp import MatchingPursuit
from mdct import Mdct

# MP METHOD EFFICIENCY

database = []
num = [25]
for k in range(len(num)):
    database.append(Database('databases/database-'+str(num[k])+'.sqlite'));



# Noise
noises = [0]

# Music library
current_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = current_dir + "/music_modif1"
music_list = []
for file in os.listdir(music_dir):
        if file.endswith(".mp3"):
                music_list.append(file)

apf = 10
duration = 2
Fe=44100
frame_size = duration*Fe//8192*8192
mdct = Mdct()
mp = MatchingPursuit(mdct,apf)
mp.buildMask(frame_size)

# pour chaque musique de la bdd on prend 3 extraits

extracts_k = [1./4,2./4,3./4]
counter = np.zeros(len(noises))
i = 0

for track in music_list:
        print(track)
        wavdata = sound.read(music_dir + "/" + track)
        lenght = wavdata.getnframes()
        fs = wavdata.getframerate()

        for coef in extracts_k:

                for k in range(len(database)):

                    for q in range(len(noises)):
                        wavdata.rewind()
                        wavdata.readframes(int(lenght*coef/(5*Fe*8192))*(5*Fe*8192))
                        db = database[k]
                        j=0
                        result = None
                        offsets = {}
                        while result == None and j < 30:
                            s = wavdata.readframes(frame_size)
                            s = np.frombuffer(s,dtype='<i2') 
                            if s.size < frame_size:
                                break
                            s = s + (2**15-1)*noises[q]* np.random.randn(frame_size)
                            song,offsets = mp.match(s,db,soffset=i*frame_size,offsets=offsets)
                            result = song
                            j=j+1
                        selected = db.getTrackTitle(song)
                        if selected != None:
                            selected = selected[0].split('/')[-1]
                        #print(selected, track[:-4])
                        if song is None:
                                print("no match")
                        else:
                                if track[:-4] == selected:
                                        print('ok')
                                        counter[q] += 1
                                else:
                                    print('non')
                i +=1

        print('\n')

print(counter,i)
f = open('result-'+str(apf),'w')
f.write(str(counter))
f.close()

