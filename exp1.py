import os
import numpy as np
import sound
import hashlib
from db import *
import matplotlib.pyplot as plt
from shazam import Shazam

# SHAZAM METHOD EFFICIENCY

database = []
database.append(Database('database1.sqlite'))
database.append(Database('database2.sqlite'))
database.append(Database('database3.sqlite'))
database.append(Database('database4.sqlite'))
database.append(Database('database5.sqlite'))

# Music library
current_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = current_dir + "/music"
music_list = []
for file in os.listdir(music_dir):
	if file.endswith(".mp3"):
		music_list.append(file)

shaz = Shazam(100)

duration = 0.2

# pour chaque musique de la bdd on prend 3 extraits
extracts_k = [1./4, 2./4, 3./4]

counter = [0, 0, 0, 0, 0]

for track in music_list:
	print track
	wavdata = sound.read(music_dir + "/" + track)
	lenght = wavdata.getnframes()
	fs = wavdata.getframerate()

	for coef in extracts_k:
		wavdata.rewind()
		wavdata.readframes(int(lenght*coef))
		keys = shaz.processTrack(wavdata, int(duration*fs))

		found_keys = {}

		for index,db in enumerate(database):
			for key in keys:
				string = str(key[0]) + '-' + str(key[1]) + '-' + str(key[2])
				offset = int(key[3])
				key_hash = hashlib.sha1(string).digest()
				key_hash = key_hash[0:5]
				key_hash = sqlite3.Binary(key_hash)
				matches = db.selectFingerprints(key_hash, 'shazam')

				for match in matches:
					if not match[0] in found_keys:
						found_keys[match[0]] = []
					found_keys[match[0]].append(match[1] - offset)

			songid = None
			max_offset = 0

			for song, offsets in found_keys.items():
			    # extract the most common offset
			    tmp_max = offsets.count(max(set(offsets), key=offsets.count))
			    if tmp_max > max_offset:
			    	max_offset = tmp_max
			    	songid = song

			if songid is None:
				print "no match"
			else:
				if track[:-4] == db.getTrackTitle(songid)[0]:
					print 'ok',
					print index,
					counter[index] += 1

	print '\n',

print counter

