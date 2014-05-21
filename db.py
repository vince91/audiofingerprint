import sqlite3

class Database:

	def __init__(self):
		self.connection = sqlite3.connect('database.db')
		self.cursor = self.connection.cursor()


	def create(self):
		"""
		"""
		self.cursor.execute('''CREATE TABLE fingerprints 
			(hash binary(128), track_id int, time int)''')
		self.cursor.execute('''CREATE INDEX id ON fingerprints (hash)''')

		self.cursor.execute('''CREATE TABLE tracks 
			(track_id INTEGER PRIMARY KEY AUTOINCREMENT, title varchar(255))''')

		self.connection.commit()

	def addTrack(self, title):
		""" Add a song to database
			return the id of the song
		"""
		self.cursor.execute("INSERT INTO tracks (title) VALUES (?)", (title,))
		self.connection.commit()

		return self.cursor.lastrowid

	def addFingerprint(self, hash, id, time):
		""" Add a finderprint to database
		"""

		self.cursor.execute("INSERT INTO fingerprints VALUES (?; ?, ?)" (hash, id, time))
		self.connection.commit()

	def selectFingerprints(self, hash):
		"""
		"""


	def __del__(self):
		self.connection.close()
