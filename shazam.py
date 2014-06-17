import numpy as np
import matplotlib.pyplot as plt

class Shazam:

	def __init__(self, window_size = 1024, frame_duration = 5):
		self.window_size = window_size
		self.hop = window_size/4
		self.window = 0.5 * (1 - np.cos(2*np.pi*np.arange(window_size)/(window_size-1)))
		self.frame_duration = frame_duration
		self.min_real = 0.0000000001

	def processTrack(self, wavdata):

		fs = wavdata.getframerate()
		track_size = wavdata.getnframes()
		frame_size = fs * self.frame_duration
		frame_number = int(track_size / frame_size)
		total_pairs = []

		if frame_number is 0:
			frame_number = 1
			frame_size = track_size

		for k in range(frame_number):
			x = wavdata.readframes(frame_size)
			x = np.frombuffer(x, dtype='<i2') 
			spect = self.spectrogram(x)
			peaks = self.findPeaks(spect)
			pairs = self.pairPeaks(peaks)

			for pair in pairs:
				f1 = pair[0][1]
				f2 = pair[1][1]
				delta_t = pair[1][0] - pair[0][0]
				offset = pair[0][0] * self.hop + k * frame_size
				total_pairs.append((f1, f2, delta_t, offset))

		return total_pairs


	def spectrogram(self, x):

		window_number = int((x.size - self.window_size) / self.hop)
		spect  = np.empty([self.window_size/2+1, window_number])

		for i in range(window_number):
			start = i * self.hop
			end = start + self.window_size
			tx = x[start:end] * self.window
			TX = np.fft.fft(tx)
			TX = TX[:self.window_size / 2 + 1]
			spect[:, i] = 10 * np.log10(np.absolute(TX) + self.min_real)

		return spect

	def findPeaks(self, spect, grid=[10, 10]):

		peaks = []

		area_height = int(spect.shape[0]/grid[0])
		area_width = int(spect.shape[1]/grid[1])

		for i in range(grid[0]):
			for j in range(grid[1]):

				area = spect[i*area_height:(i+1)*area_height, j*area_width:(j+1)*area_width]
				max_y, max_x = np.unravel_index(area.argmax(), area.shape)

				max_y += i*area_height
				max_x += j*area_width#*self.hop

				peaks.append([max_x, max_y])

		return np.array(peaks)

	def pairPeaks(self, peaks, max_distance = 100):

		pairs = []

		for peak_orig in peaks:
			for peak in peaks:
				if peak[0] > peak_orig[0]:
					if np.linalg.norm(peak_orig - peak) <= max_distance:
						pairs.append([peak_orig, peak])


		return pairs


