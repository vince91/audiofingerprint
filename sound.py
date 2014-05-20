import pyaudio
from array import array
import sys
import numpy

class Sound:
	
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100

	def __init__(self, duration = 5):
		self.duration = duration

	def record(self):
		"""
		record a sound from the microphone
		"""
		print('Recording a %d seconds sound' % self.duration);

		self.samples = array('h')

		p = pyaudio.PyAudio();
		stream = p.open(format = self.FORMAT, channels = self.CHANNELS, rate = self.RATE, input = True, frames_per_buffer = self.CHUNK)

		for i in range(0, int(self.duration * self.RATE / self.CHUNK)):
			data = array('h', stream.read(self.CHUNK))
			if sys.byteorder == 'big':
				data.byteswap()
			self.samples.extend(data)

		stream.stop_stream()
		stream.close()
		p.terminate()


	def save(self):

		numpy.savetxt("foo.csv", self.samples, delimiter=",")






