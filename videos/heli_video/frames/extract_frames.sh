#!/usr/bin/env bash

ffmpeg -i ../6015_20210507_HelicopterFliesOnMars-1280.m4v -qscale:v 2 %d.jpg
