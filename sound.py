import pyaudio
from array import array
import sys
import numpy
from tempfile import NamedTemporaryFile
import subprocess
import wave as wv
from StringIO import StringIO
import os

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




def read(filename):

	file = open(filename,'rb')
	input_file = NamedTemporaryFile(mode='wb')
	input_file.write(file.read())
	input_file.flush()
	output_file = NamedTemporaryFile(mode="rb")
	args = ["ffmpeg" , "-y" ,  "-i" , input_file.name , "-f" , "wav", output_file.name]
	# process ffmpeg
	subprocess.call(args,stderr=open(os.devnull))
	
	wavdata = wv.open(StringIO(output_file.read()),'rb')
	input_file.close()
	output_file.close()

	return wavdata



