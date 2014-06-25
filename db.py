import sqlite3

class Database:

	def __init__(self, filename):
		self.connection = sqlite3.connect(filename)
		self.connection.text_factory = str
		self.cursor = self.connection.cursor()

	def create(self):
		"""
		"""
		self.cursor.execute('''CREATE TABLE fingerprints_mp 
			(hash BINARY(40), track_id INTEGER, offset INTEGER)''')
		
		self.cursor.execute('''CREATE INDEX id_mp ON fingerprints_mp (hash)''')

		self.cursor.execute('''CREATE TABLE fingerprints_shazam 
			(hash BINARY(40), track_id INTEGER, offset INTEGER)''')

		self.cursor.execute('''CREATE INDEX id_shazam ON fingerprints_shazam (hash)''')

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

	def addFingerprint(self, query, type = 'mp'):
		""" Add a finderprint to database
		"""
		self.cursor.executemany("INSERT INTO fingerprints_%s VALUES (?, ?, ?)" % type, (query))
		self.connection.commit()

	def selectFingerprints(self, hash, type = 'mp'):
		"""
		"""
		self.cursor.execute("SELECT track_id, offset FROM fingerprints INDEXED BY id WHERE hash=?" , (sqlite3.Binary(hash),))
		return self.cursor.fetchall()

	def getTrackNumber(self):
		"""
		"""
		self.cursor.execute('SELECT COUNT(*) FROM tracks')
		return self.cursor.fetchone()

	def getTrackTitle(self, id):
		"""
		"""
		self.cursor.execute('SELECT title FROM tracks WHERE track_id=?', (id,))
		return self.cursor.fetchone()

	def selectTrack(self, title):
		"""
		"""
		self.cursor.execute('SELECT track_id FROM tracks WHERE title=?', (title,))
		return self.cursor.fetchone()

	def __del__(self):
		self.connection.close()
