import os
import sound
import hashlib
from db import Database
from mp import MatchingPursuit
from mdct import Mdct
import numpy as np
from  sqlite3 import Binary

current_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = os.path.join(current_dir, 'music')
music_list = []

# Selecting all mp3 in music directory
for dirpath,dirnames,filenames in os.walk(music_dir, followlinks=True):
    for filename in filenames:
        music_list.append(os.path.join(dirpath,filename))

print("%d tracks in database" % len(music_list))

# Creating an empty database
if os.path.isfile(current_dir + "/database.sqlite"):
        os.remove(current_dir + "/database.sqlite")
database = Database()
database.create()
del database

# Processing each track

atoms_per_frame = 20
frame_duration = 5

mdct = Mdct()
mp = MatchingPursuit(mdct, atoms_per_frame)
biggest_atom_size = mdct.sizes[-1]
Fe = 44100
frame_size = int(frame_duration*Fe/biggest_atom_size)*biggest_atom_size
mp.buildMask(frame_size)

for track in music_list:
    query = []
    track_title = track[:-4]

    database = Database()
    track_id = database.addTrack(track_title)
    del database
    print("=> Processing %s, id: %d" % (track_title, track_id))

    wavdata = sound.read(track)
    Fe = wavdata.getframerate()
    frame_number = int(wavdata.getnframes()/frame_size)

    print("%d frames to process for this track" % frame_number)
    
    progress = 0

    for i in range(frame_number):
        s = wavdata.readframes(frame_size)
        s = np.frombuffer(s, dtype='<i2') 
        y = mp.sparse(s)
        keys = mp.extractKeys(y)
        query.extend([(Binary(hash_key)[0:5],track_id, int(i*frame_size+offset)) for (hash_key,offset) in keys])


        if i*100/frame_number >= progress + 10:
            progress = i * 100/frame_number
        #print("%d%%," % (progress,)),
    

    database = Database()
    database.addFingerprint(query)
    del database

    print("100%")











