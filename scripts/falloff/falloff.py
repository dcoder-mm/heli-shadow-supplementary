#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

filename = sys.argv[1]
im = Image.open(filename).convert('L')
w,h = im.size
im.resize((im.size[0],1), Image.ANTIALIAS)

fig, ax1 = plt.subplots()
plt.title("%s (%dx%d)"%(filename, w, h))
plt.xlabel("X-coordinate [pixels]")
plt.ylabel("Luminosity (0-255)")
ax1.plot(np.arange(im.size[0]), np.asarray(im).mean(axis=0))
plt.show()