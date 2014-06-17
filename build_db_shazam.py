import os
import sound
import hashlib
import sqlite3
from db import Database
from shazam import Shazam


current_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = current_dir + "/music"
music_list = []

if os.path.isfile(current_dir + "/database.sqlite"):
	os.remove(current_dir + "/database.sqlite")
database = Database()
database.create()

for file in os.listdir(music_dir):
	if file.endswith(".mp3"):
		music_list.append(file)
print("%d tracks in database" % len(music_list))

shazam = Shazam()

for track in music_list:
	track_title = track[:-4]
	track_id = database.addTrack(track_title)
	print("=> Processing %s, id: %d" % (track_title, track_id))

	wavdata = sound.read(music_dir + "/" + track)
	keys = shazam.processTrack(wavdata)

	print("=> %d keys" % len(keys))

	query = []
	for key in keys:
		string = str(key[0]) + '-' + str(key[1]) + '-' + str(key[2])
		offset = int(key[3])
		key_hash = hashlib.sha1(string).digest()
		key_hash = sqlite3.Binary(key_hash)
		query.append((key_hash, track_id, offset))

	database.addFingerprint(query, 'shazam')



