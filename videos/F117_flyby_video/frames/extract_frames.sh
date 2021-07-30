#!/usr/bin/env bash

ffmpeg -i ../F117_flyby.mp4 -qscale:v 2 %d.jpg
