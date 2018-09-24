# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 22:14:17 2018

@author: Dave
"""

import random
import glob
import time
import re
import sys
import subprocess

hauntIntervalMin = 0
hauntIntervalMax = 0
playlistMode = 0
soundIndex = 0
duration = 0
sounds = sorted(glob.glob("sound_library/*"))

# maybe add safeguard here so only audio files are added to list
def configure():
    with open("ghost_config.txt","r") as config:
        configLines = config.readlines()
    global hauntIntervalMin
    global hauntIntervalMax
    global playlistMode
    for line in configLines:
        if "maximum_time" in line:
            hauntIntervalMax = int(re.findall(r"\d+",line)[0])
        if "minimum_time" in line:
            hauntIntervalMin = int(re.findall(r"\d+",line)[0])
        if "playlist_mode" in line:
            playlistMode = int(re.findall(r"\d+",line)[0])
        if "total_duration" in line:
            duration = int(re.findall(r"\d+",line)[0])
    if playlistMode < 3:
        random.shuffle(sounds)

# Play random noise using whatever native audio player your system comes with. Uses
# code from https://gist.github.com/juancarlospaco/c295f6965ed056dd08da
def randomNoise():
    if playlistMode == 0:
        sound =  sounds[random.randint(0,len(sounds)-1)]
    else:
        sound =  sounds[soundIndex]

    if sys.platform.startswith("linux"):
        return subprocess.call("chrt -i 0 aplay " + sound)
    if sys.platform.startswith("darwin"):
        return subprocess.call("afplay " + sound)
    if sys.platform.startswith("win"):  
        return subprocess.call("start /low /min " + sound)

def checkPlaylist():
    if soundIndex == len(sounds):
        global soundIndex
        soundIndex = 0
        if playlistMode == 1:
            random.shuffle(sounds)

# Our main function, which schedules the random noises and calls the associated
# functions. It also checks the execution timer to know when to quit.
def haunt(tMin,tMax):
    running = 1
    timer_start = time.time()
    global soundIndex
    global relayIndex
    while running:
        schedule = random.randint(tMin,tMax)
        if duration > 0:
            if time.time() - timer_start + schedule >= duration:
                schedule = duration - (time.time() - timer_start)
                running = 0
        time.sleep(schedule)
        randomNoise()
        soundIndex += 1
        checkPlaylist()
        if duration > 0:
            if time.time() - timer_start >= duration:
                running = 0
configure()
print(hauntIntervalMin)
print(hauntIntervalMax)
haunt(hauntIntervalMin,hauntIntervalMax)
