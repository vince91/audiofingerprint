import sqlite3

class Database:

	def __init__(self):
		self.connection = sqlite3.connect('database.db')
		self.connection.text_factory = str
		self.cursor = self.connection.cursor()


	def create(self):
		"""
		"""
		self.cursor.execute('''CREATE TABLE fingerprints 
			(hash BINARY(160), track_id INTEGER, frame INTEGER, time INTEGER)''')
		self.cursor.execute('''CREATE INDEX id ON fingerprints (hash)''')

		self.cursor.execute('''CREATE TABLE tracks 
			(track_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)''')

		self.connection.commit()

	def addTrack(self, title):
		""" Add a song to database
			return the id of the song
		"""
		self.cursor.execute("INSERT INTO tracks (title) VALUES (?)", (title,))
		self.connection.commit()

		return self.cursor.lastrowid

	def addFingerprint(self, hash, id, frame, time):
		""" Add a finderprint to database
		"""
		self.cursor.execute("INSERT INTO fingerprints VALUES (?, ?, ?, ?)", (sqlite3.Binary(hash), id, frame, time))
		self.connection.commit()

	def selectFingerprints(self, hash):
		"""
		"""


	def __del__(self):
		self.connection.close()
