import os
from db import Database

current_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = current_dir + "/music"
music_list = []

# Selecting all mp3 in music directory
for file in os.listdir(music_dir):
	if file.endswith(".mp3"):
		music_list.append(file)

print("%d tracks in database" % len(music_list))

# Creating an empty database
if os.path.isfile(current_dir + "/database.db"):
	os.remove(current_dir + "/database.db")
database = Database()
database.create()

# Processing each track
for track in music_list:
	track_title = track[:-4]
	track_id = database.addTrack(track_title)
	print("Processing %s, id: %d" % (track_title, track_id))

