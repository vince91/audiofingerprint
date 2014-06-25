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
num = [10,15,20,25,30,35,40,50,60,70,80,90]
for k in range(len(num)):
    database.append(Database('databases/database-'+str(num[k])+'.sqlite'));

# Music library
current_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = current_dir + "/music"
music_list = []
for file in os.listdir(music_dir):
        if file.endswith(".mp3"):
                music_list.append(file)

apf = 10
duration = 5
Fe=44100
frame_size = duration*Fe//8192*8192
mdct = Mdct()
mp = MatchingPursuit(mdct,apf)
mp.buildMask(frame_size)

# pour chaque musique de la bdd on prend 3 extraits
extracts_k = [1./4, 2./4, 3./4]

counter = np.zeros(len(num))
i = 0

for track in music_list:
        print(track)
        wavdata = sound.read(music_dir + "/" + track)
        lenght = wavdata.getnframes()
        fs = wavdata.getframerate()

        for coef in extracts_k:
                wavdata.rewind()
                wavdata.readframes(int(lenght*coef))
                s = wavdata.readframes(frame_size)
                s = np.frombuffer(s,dtype='<i2')

                for k in range(len(database)):
                    db = database[k]
                    song,offset = mp.match(s,db)
                    selected = db.getTrackTitle(song)
                    if selected != None:
                        selected = selected[0].split('/')[-1]
                    #print(selected, track[:-4])
                    if song is None:
                            print("no match")
                    else:
                            if track[:-4] == selected:
                                    print('ok')
                                    counter[k] += 1
                i +=1

        print('\n')

print(counter,i)

