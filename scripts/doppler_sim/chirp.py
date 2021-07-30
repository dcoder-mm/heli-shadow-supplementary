#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import chirp
from scipy.io.wavfile import write

duration = 30 
Fs = 16000
freqs = [100, 100.5, 99, 99.3, 100.1, 100]

segment = int(Fs * duration / (len(freqs)-1))
f = np.array(freqs) / Fs
wav = np.array(1)

phase = 0
for f0, f1 in zip(f[:-1], f[1:]):
	wav = np.append(wav, chirp(np.arange(segment), f0=f0, t1=segment, f1=f1, phi=phase))
	phase = phase + 360*(segment*(f0+f1)/2)

write('test3.wav', Fs, wav)
