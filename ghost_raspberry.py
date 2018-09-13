# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 22:14:17 2018

@author: Dave
"""

import random
import glob
import time
import re
from subprocess import Popen

hauntIntervalMin = 0
hauntIntervalMax = 0
hauntMode = 0
playlistMode = 0
playlistIndex = 0
duration = 0

sounds = sorted(glob.glob("sound_library/*"))

# maybe add safeguard here so only audio files are added to list
def configure():
    with open("ghost_config.txt","r") as config:
        configLines = config.readlines
    global hauntIntervalMin
    global hauntIntervalMax
    global hauntMode
    global playlistLoop
    for line in configLines:
        if "maximum_time" in line:
            hauntIntervalMax = re.findall(r"\d+",line)[0]
        if "minimum_time" in line:
            hauntIntervalMin = re.findall(r"\d+",line)[0]
        if "activation_mode" in line:
            hauntMode = re.findall(r"\d+",line)[0]
        if "playlist_Mode" in line:
            playlistLoop = re.findall(r"\d+",line)[0]
        if "total_duration" in line:
    if playlistMode !=2:
        random.shuffle(sounds)
        
def randomNoise():
    global sounds
    if playlistMode == 0:
        Popen("omxplayer", sounds[random.randint(0,len(sounds)-1)])
    if playlistMode == 1 or playlistMode == 2:
        global playlistIndex
        if playlistIndex == len(sounds):
            playlistIndex = 0
            if playlistMode == 1:
                random.shuffle(sounds)
        Popen("omxplayer", sounds[playlistIndex])

def relayTrigger():
    # code goes here
def haunt(tMin,tMax):
    global hauntMode
    global duration
    running = 1
    timer_start = time.time()
    while running:
        schedule = random.randint(tMin,tMax)
        if duration > 0:
            if time.time() - timer_start + schedule >= duration:
                schedule = duration - (time.time() - timer_start)
                running = 0
        time.sleep(schedule)
        if hauntMode == 0:
            randomNoise()
        if hauntMode == 1:
            coinflip = random.randint(1,2)
            if coinflip == 1:
                randomNoise()
            if coinflip == 2:
                relayTrigger()
        if duration > 0:
            if time.time() - timer_start >= duration:
                running = 0
                
                
    
