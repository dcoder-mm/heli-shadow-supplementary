#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from  progressbar import progressbar

blade1 = Image.open("blade480.png").convert("RGBA")
blade2 = blade1.transpose(Image.FLIP_TOP_BOTTOM)
box = Image.open("box480.png").convert("RGBA")
background = Image.open("sand.jpg").convert("RGBA")

w,h = blade1.size
center = (w//2, h//2)

#box = box.rotate(-13, center=center)

#background = Image.new("RGBA", (w,h), (170,170,170,255))

Trow = 19
gain_correction = 1


show_textbox = True
textbox_pos = 'BL'

show_text_exposure = True
show_text_readout = True
show_text_hold = True
show_text_pls = True
show_text_RPM = False
show_text_angles = False
show_text_alpha = False
show_text_cy = False
show_text_scale = False


def single_exposure(cx, cy, scale, a1, a2, shadow_alpha, gain):
	bg = background.copy()
	shape = blade1.rotate(a1, center=center)
	t = blade2.rotate(a2, center=center)
	shape.paste(t, (0,0), t)
	shape.paste(box, (0,0), box)
	if scale != 1:
		shape = shape.resize((int(w*scale), int(h*scale)), Image.NEAREST)

	data = np.array(shape)  
	r, g, b, a = data.T 
	black = (r == 0) & (g == 0) & (b == 0) & (a == 255)
	data[..., :][black.T] = (0, 0, 0, shadow_alpha*255)
	shape = Image.fromarray(data)

	bg.paste(shape, (int(w/2 - w*scale/2 + cx), int(h/2 - h*scale/2 + cy)), shape)
	return np.array(bg.convert("L")) * gain



def construct_frame(exposure_us, RPM, PLS, a1, a2, readout_us=h*Trow, 
					shadow_alpha=0.6, gain=None, hold_us=0, cy=0, cx=0, scale=1):
	degrees_per_trow = RPM/60E6*360*Trow
	exposure_trows = exposure_us//Trow
	hold_trows = int(hold_us//Trow)	
	kReadout = readout_us/h/Trow

	if gain==None:
		gain = 1/(exposure_trows + hold_trows/PLS + (h/2)/PLS*kReadout) * gain_correction

	sensor = np.zeros((w,h))

	if exposure_us != 0:	
		print("Building Base image")
		for i in progressbar(range(exposure_trows)):
			sensor += single_exposure(cx, cy, scale, a1, a2, shadow_alpha, gain)
			a1 += degrees_per_trow
			a2 -= degrees_per_trow	

	if hold_trows != 0:
		print("Building Hold image")
		for i in progressbar(range(hold_trows)):
			sensor += single_exposure(cx, cy, scale, a1, a2, shadow_alpha, gain) / PLS
			a1 += degrees_per_trow
			a2 -= degrees_per_trow		

	if readout_us != 0:
		print("Applying PLS frames")
		PLS_frames = []
		for line in progressbar(range(h)):
			PLS_frames.append(single_exposure(cx, cy, scale, a1 ,a2, shadow_alpha, gain) / PLS * kReadout)
			for t in range(-1, -line-1, -1):
				sensor[line,:] += PLS_frames[t][line,:]
			a1 += degrees_per_trow * kReadout
			a2 -= degrees_per_trow * kReadout
		
	return Image.fromarray(np.uint8(np.clip(sensor, a_min=0, a_max=255)), 'L')		



def frame(exposure_us, RPM, PLS, readout_us=h*Trow, shadow_alpha=0.715, 
		a1=-35, a2=90, gain=None, cy=0, cx=0, scale=1, hold_us=0):
	filename = "./out/exp%d_readout%d_hold%d_PLS%d_alpha%.2f_RPM%d_a1=%d_a2=%d_cy%d_scale%.2f.png"%(exposure_us, readout_us, hold_us, PLS, shadow_alpha, RPM, a1, a2, cy, scale)
	if os.path.isfile(filename):
		print("Skipping "+filename)
		return -1
	text =  "RPM = %d \n" % (RPM) 								if show_text_RPM else ""
	text += "Exposure = %dus \n" % (exposure_us)				if show_text_exposure else ""
	text += "Hold = %dus \n" % (hold_us) 						if show_text_hold else ""
	text += "Readout = %dus \n" % (readout_us) 					if show_text_readout else ""
	text += "1/PLS = %d (GSE %.2f%%) \n" % (PLS, 100-(100/PLS))	if show_text_pls else ""
	text += "a1 = %d°, a2 = %d° \n" % (a1, a2)					if show_text_angles else ""
	text += "Y position = %d \n" % (cy)							if show_text_cy else ""
	text += "Scale = %.2f \n" % (scale)							if show_text_scale else ""
	text += "Shadow density = %.2f \n" % (shadow_alpha) 		if show_text_alpha else ""
	print(text)	
	im = construct_frame(exposure_us = exposure_us, RPM=RPM, PLS=PLS, hold_us=hold_us,
						readout_us=readout_us, shadow_alpha=shadow_alpha, 
						a1=a1, a2=a2, gain=gain, scale=scale, cy=cy, cx=cx).convert("LA")
	im = im.filter(ImageFilter.GaussianBlur(0.75))
	if show_textbox:
		draw = ImageDraw.Draw(im)
		font = ImageFont.truetype("Helvetica.ttc", 12)
		tw, th = font.getsize_multiline(text)
		tx = 2
		ty = 2
		if textbox_pos in ['BL', 'BR']: ty = h - th - 2
		if textbox_pos in ['TR', 'BR']: tx = w - tw - 2			
		draw.rectangle((tx, ty, tx+tw+16, ty+th+16), fill='black')
		draw.text((tx+8, ty+8), text, font=font)
	im.save(filename)
	im.close()
	print()


# a1 = -90
# a2 = 90
# RPM = 2500
# degrees_per_us = RPM/60E6*360

# for i in range(90):
# 	frame(a1=a1, a2=a2, exposure_us=11, RPM=RPM, PLS=63, readout_us=0)
# 	frame(a1=a1, a2=a2, exposure_us=5400, RPM=RPM, PLS=63, readout_us=0)
# 	frame(a1=a1, a2=a2, exposure_us=133, RPM=RPM, PLS=63, readout_us=5400)
# 	a2 -= 1;
# 	a1 += 1;

# quit()

# construct_frame(exposure_us=133, RPM=2500, PLS=48, readout_us=5400, hold_us=0, a1=-35, a2=90).save("test.png")
# quit()
# show_textbox = False
# gain_correction = 1.0

# 1
#frame(a1=-15, a2=-90, cy=10, scale=0.6, exposure_us=133, hold_us=0, RPM=2537, PLS=100, readout_us=9272, shadow_alpha=0.6)

# 2
#frame(a1=-5, a2=-55, cy=0, cx=30, scale=2.3, exposure_us=133, hold_us=0, RPM=2537, PLS=100, readout_us=9272, shadow_alpha=0.6)

# 3
#frame(a1=90-4, a2=90+4, cy=20, cx=0, scale=0.8, exposure_us=133, hold_us=0, RPM=2537, PLS=100, readout_us=9272, shadow_alpha=0.6)

# 4
frame(a1=90-50, a2=90+10, cy=30, cx=0, scale=0.8, exposure_us=133, hold_us=0, RPM=2537, PLS=80, readout_us=9272, shadow_alpha=0.6)


#frame(a1=0, a2=90, exposure_us=133, hold_us=0, RPM=2537, PLS=80, readout_us=9272)


quit()

a1 = 45
a2 = 90

scale_variants = [1]
cy_variants = [0]

exposure_variants = [0]
PLS_variants = [100]
readout_variants = np.linspace(0, 9272*2, 300)
hold_variants = [0]
#PLS_variants.extend(range(10, 2000, 10))


nvariants =  len(exposure_variants)
nvariants *= len(PLS_variants) 
nvariants *= len(hold_variants) 
nvariants *= len(readout_variants) 
nvariants *= len(scale_variants)
nvariants *= len(cy_variants)

cnt = 0
for cy in cy_variants:
	for scale in scale_variants:
		for hold_us in hold_variants:
			for exposure_us in exposure_variants:
				for PLS in PLS_variants:
					for readout_us in readout_variants:
						cnt+=1
						print("Variant %d / %d"%(cnt, nvariants))
						frame(exposure_us=exposure_us, RPM=2500, PLS=PLS, 
							readout_us=readout_us, hold_us=hold_us, scale=scale, 
							cy=cy, a1=a1, a2=a2, shadow_alpha = 0.6)

