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
			(hash BINARY(160), track_id INTEGER, offset INTEGER)''')
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

	def addFingerprint(self, query):
		""" Add a finderprint to database
		"""
		self.cursor.executemany("INSERT INTO fingerprints VALUES (?, ?, ?)", (query))
		self.connection.commit()

	def selectFingerprints(self, hash):
		"""
		"""
		self.cursor.execute('SELECT track_id, offset FROM fingerprints INDEXED BY id WHERE hash=?', (hash,))

		return self.cursor.fetchall()

	def getTrackNumber(self):
		"""
		"""
		self.cursor.execute('SELECT COUNT(*) FROM tracks')
		return self.cursor.fetchone()



	def __del__(self):
		self.connection.close()
