#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import sweep_poly
from PIL import Image, ImageDraw

# Ground truth from https://mars.nasa.gov/mars2020/mission/where-is-the-rover/ 
meters_per_pixel = 50/167
rover = np.array([740, 274, 0])*meters_per_pixel
heli_p1 = np.array([501,209, 5])*meters_per_pixel
heli_p2 = np.array([573, 653, 5])*meters_per_pixel
heli_p3 = np.array([520, 210, 5])*meters_per_pixel
title = "Ingenuity 4th flight. BPF tone Doppler shift simulation"

# rover = np.array([740, 274, 0])*meters_per_pixel
# heli_p1 = np.array([501,209, 5])*meters_per_pixel
# heli_p2 = np.array([457, 653, 5])*meters_per_pixel
# heli_p3 = np.array([520, 210, 5])*meters_per_pixel
# title = "10° test"

# rover = np.array([740, 274, 0])*meters_per_pixel
# heli_p1 = np.array([520, 210, 5])*meters_per_pixel
# heli_p2 = np.array([531, 306, 5])*meters_per_pixel
# heli_p3 = np.array([633, 639, 5])*meters_per_pixel
# title = "Offscreen 10° turn"

# meters_per_pixel=1.0
# rover = np.array([0, 0, 0])*meters_per_pixel
# heli_p1 = np.array([5000.0,200, 200])*meters_per_pixel
# heli_p2 = np.array([-3000.0, 200, 200])*meters_per_pixel
# title = "Flyby, 200m above, 200m sideways, 200m/s"


heli_pos = heli_p1.copy()
heli_direction = np.zeros(3)
heli_target = heli_p2

heli_speed = 0
heli_vel = 0

dt = 0.1

hover_time_at_liftoff = 10
hover_time_at_landing = 10
hover_time_at_p2 = 3

accel_time = 10
max_speed = 3.5

center_freq = 84.36
speed_of_sound = 250

do_map = True
rovel_color = (220,20,20)
heli_color = (20,20,220)
r = 5

points = []

time = 0.0

dist_p1 = np.linalg.norm(rover-heli_p1)
print("Rover-Heli dist @ start: %.1f meters, sound lag %.2f sec"%( dist_p1, dist_p1/speed_of_sound ))
dist_p2 = np.linalg.norm(rover-heli_p2)
print("Rover-Heli dist max: %.1f meters, sound lag %.2f sec"%( dist_p2, dist_p2/speed_of_sound ))
print("p1-p2 trip: %.1f meters"%( np.linalg.norm(heli_p1-heli_p2) ))
print("p2-p3 trip: %.1f meters"%( np.linalg.norm(heli_p2-heli_p3) ))


if do_map:
	flight_map = Image.open("flight_map.jpg")
	draw = ImageDraw.Draw(flight_map)
	p = rover / meters_per_pixel
	draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill = rovel_color, outline ='black')




def set_target(p):
	global heli_direction, heli_target
	heli_target = p
	v = p - heli_pos
	heli_direction = v/np.linalg.norm(v)

def update_heli():
	global heli_pos, heli_vel, points, time
	heli_vel = heli_direction * heli_speed
	heli_pos += heli_vel*dt

	d1 = np.linalg.norm(rover-heli_pos)
	d2 = np.linalg.norm(rover-(heli_pos+heli_vel*dt))
	sh = (d2 - d1)/dt
	fo = center_freq*(speed_of_sound)/(speed_of_sound+sh)
	print("%.1fs\t%.1fm\t%.1fm/s\t%.1fm/s\t%.1fHz"%(time, d1, heli_speed, sh, fo))
	points.append(fo)

	if do_map:
		m = flight_map.copy()
		draw = ImageDraw.Draw(m)
		p = heli_pos / meters_per_pixel
		draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill = heli_color, outline ='black')
		m.save("./frames/%d.jpg"%(int(time*10)), quality=95)
		m.close()
	time += dt

def hover(s):
	for i in range(int(s/dt)):
		update_heli()

def accelerate(speed, time, k=1):
	global heli_speed
	for i in range(int(time/dt)):
		heli_speed+=speed/(time/dt)*k
		update_heli()	

def decelerate(target_speed, time):
	accelerate(heli_speed-target_speed, time, k=-1)

def free_flight(warn_time):
	while True:
		braking_dist = heli_speed/2*warn_time
		update_heli()
		if np.linalg.norm(heli_pos-heli_target)<braking_dist:
			break


# ~~~~~~ Ground truth
hover(hover_time_at_liftoff) # Hovering at p1

set_target(heli_p2)
accelerate(max_speed, accel_time) # Accelerating at p1

free_flight(accel_time) # Flying to p2

decelerate(0, accel_time) # Decelerating at p2
hover(hover_time_at_p2) # Hovering at p2

set_target(heli_p3) # Going home
accelerate(max_speed, accel_time) # Accelerating at p2
	
free_flight(accel_time) # Flying to p3	

decelerate(0, accel_time) # Decelerating at p3
hover(hover_time_at_landing) # Hovering at p3

# ~~~~~~ 10° offscreen turn
# hover(hover_time_at_liftoff) 

# set_target(heli_p2)
# accelerate(max_speed, accel_time) 

# free_flight(0.5) 
# set_target(heli_p3)
# free_flight(accel_time)

# decelerate(0, accel_time) 
# hover(hover_time_at_p2) 

# set_target(heli_p2) 
# accelerate(max_speed, accel_time) 

# free_flight(0.5) 
# set_target(heli_p1)	
# free_flight(accel_time)

# decelerate(0, accel_time) 
# hover(hover_time_at_landing) 


# ~~~~~~ Flyby 200m/s
# set_target(heli_p2)
# accelerate(200, 1) 
# free_flight(1)

plt.figure(figsize=(12, 6), dpi=100)
plt.title(title)
plt.xlabel("Time (s)")
plt.ylabel("BPF1 tone (Hz)")
plt.axhline(y=center_freq, color='g', linestyle='--', linewidth=1)
plt.plot(np.linspace(0, len(points)*dt, len(points)), points)
plt.show()



