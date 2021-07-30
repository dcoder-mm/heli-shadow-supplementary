#!/usr/bin/env bash

ffmpeg -i ../ov7251_7000RPM_Exp1.mkv -qscale:v 2 %d.jpg
