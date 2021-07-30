#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

samplerate, wave = wavfile.read(sys.argv[1])

win_size = 10 * samplerate
win_step = int(1 * samplerate)

center_f_hz = 84.36
speed_of_sound_ms = 240

times = []
peak_f = []
speed = []

for i in range(0, int((len(wave)-win_size)/win_step)):
	win_start = i*win_step
	win_stop = win_start + win_size

	window = np.zeros(2**(int(np.ceil(np.log2(win_size)))))
	window[0:win_size] = wave[win_start:win_stop, 0]

	fourier = np.fft.fft(window)

	idx = np.argmax(np.abs(fourier))
	freqs = np.fft.fftfreq(len(fourier))
	freq = freqs[idx]
	freq_in_hertz = abs(freq * samplerate)

	t = (win_start+win_size/2)/samplerate
	print("%.1f seconds: %.3f"%(t, freq_in_hertz))

	times.append(t)
	peak_f.append(freq_in_hertz)
	speed.append( speed_of_sound_ms * (center_f_hz - freq_in_hertz)/freq_in_hertz)

plt.figure(figsize=(12, 6), dpi=100)
plt.title("Ingenuity 4th flight. Relative Speed from Doppler shift")
plt.xlabel("Time (s)")

# plt.ylabel("BPF1 tone (Hz)")
# plt.plot(times, peak_f)
# plt.show()	
# quit()

plt.axhline(y=0, color='g', linestyle='--', linewidth=1)
plt.ylabel("Relative speed (m/s)")
plt.plot(times, speed)
plt.show()	
