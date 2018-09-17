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
from multiprocessing.dummy import Process
import RPi.GPIO as GPIO


hauntIntervalMin = 0
hauntIntervalMax = 0
hauntMode = 0
playlistMode = 0
soundIndex = 0
relayIndex = 0
relayTiming = [1,1,1,1,1,1]
relayPlaylistMode = 0
soundRelayPair = []
relayPlaylist = []
outPin = 17
duration = 0
sounds = sorted(glob.glob("sound_library/*"))

def configRelayPlaylist():
    with open("GPIO_playlist.txt", "r") as rp:
        lines = rp.readlines()
    firstLine = 0
    for lineNum, line in enumerate(lines):
        if "#" not in line and re.search(r"\d+,", line):
            firstLine = lineNum
            break
    lines = lines[firstLine:]
    lines = [x.strip() for x in lines if re.search(r"\d+,", x)]
    for index, line in enumerate(lines):
        line = line.split(",")
        line = [float(x) for x in line]
        relayPlaylist.append(line)
    if hauntMode == 3:
        global soundRelayPair
        if len(sounds) != len(relayPlaylist):
            print("You don't have a GPIO setting for every sound or " +
                  "vice-versa. One of the two playlists will be truncated.")
        soundRelayPair = list(zip(sounds,relayPlaylist))

# maybe add safeguard here so only audio files are added to list
def configure():
    with open("ghost_config.txt","r") as config:
        configLines = config.readlines()
    global hauntIntervalMin
    global hauntIntervalMax
    global hauntMode
    global playlistMode
    global relayTiming
    global relayPlaylistMode
    global outPin
    for line in configLines:
        if "maximum_time" in line:
            hauntIntervalMax = int(re.findall(r"\d+",line)[0])
        if "minimum_time" in line:
            hauntIntervalMin = int(re.findall(r"\d+",line)[0])
        if "activation_mode" in line:
            hauntMode = int(re.findall(r"\d+",line)[0])
        if "playlist_mode" in line:
            playlistMode = int(re.findall(r"\d+",line)[0])
        if "total_duration" in line:
            duration = int(re.findall(r"\d+",line)[0])
        if "board_out" in line:
            outPin = int(re.findall(r"\d+", line)[0])
        if "GPIO_playlist_mode" in line:
            relayPlaylistMode = int(re.findall(r"\d+", line)[0])

    configRelayPlaylist()
    if playlistMode < 3:
        random.shuffle(soundRelayPair)
        random.shuffle(sounds)
        random.shuffle(relayPlaylist)
    if hauntMode == 3:
        global sounds
        global relayPlaylist
        sounds,relayPlaylist = zip(*soundRelayPair)
# Here we use the Raspberry Pi's onboard omxplayer to deal with any number of
# media files. Depending on the playlistMode, we either do a random sound,
# the next sound from a random playlist (to ensure no repeats), or the next
# sound in the sorted playlist order.

# This should all work over HDMI as well, which may be more convenient for
# people and even opens up the possibility of video or even projection.
# Something for future work.
def randomNoise():
    if playlistMode == 0:
        Popen(["omxplayer", sounds[random.randint(0,len(sounds)-1)]])
    if playlistMode > 0:
        Popen(["omxplayer", sounds[soundIndex]])


# Trigger an electrical relay with the pi's GPIO pins. For now we just have one
# output but we could add more, and even randomize which gets triggered.
def relayTrigger(pin):
# We'll have to check how fast the setup process is. We might not want
# to do this every time, just once at the beginning of the haunt().
    if relayPlaylistMode == 0:
        timing = relayPlaylist[random.randint(0,len(relayPlaylist)-1)]
    if relayPlaylistMode > 0:
        timing = relayPlaylist[relayIndex]
    print("Timing is ")
    print(timing)
    print("Pin is " + str(pin))
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    if len(timing)%2 != 0:
        timing.append(1)
    for on, off in zip(timing[0::2],timing[1::2]):
        if on < 0.05:
            on = 0.05
        if off < 0.05:
            off = 0.05
        GPIO.output(pin, True)
        time.sleep(on)
        GPIO.output(pin, False)
        time.sleep(off)
    GPIO.cleanup()

def checkPlaylist():
    if hauntMode != 3:
        if soundIndex == len(sounds):
            global soundIndex
            soundIndex = 0
            if playlistMode == 1:
                random.shuffle(sounds)
        if relayIndex == len(relayPlaylist):
            global relayIndex
            relayIndex = 0
            if relayPlaylistMode == 1:
                random.shuffle(relayPlaylist)
    if hauntMode ==3:
        if soundIndex == len(soundRelayPair) or relayIndex == len(soundRelayPair):
            global soundIndex
            global relayIndex
            global soundRelayPair
            global sounds
            global relayPlaylist
            soundIndex = 0
            relayIndex = 0
            if playlistMode == 1:
                random.shuffle(soundRelayPair)
                sounds,relayPlaylist = zip(*soundRelayPair)


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
        if hauntMode == 0:
            randomNoise()
            soundIndex += 1
            checkPlaylist()
        if hauntMode == 1:
            coinflip = random.randint(1,2)
            if coinflip == 1:
                randomNoise()
                soundIndex += 1
            if coinflip == 2:
                relayTrigger(outPin)
                relayIndex += 1
            checkPlaylist()
        if hauntMode == 2 or hauntMode == 3:
            global outPin
            doSound = Process(target = randomNoise)
            doRelay = Process(target = relayTrigger, args = [outPin])
            doSound.start()
            doRelay.start()
            doSound.join()
            doRelay.join()
            soundIndex += 1
            relayIndex += 1
            checkPlaylist()
        if hauntMode == 4:
            relayTrigger(outPin)
            relayIndex += 1
            checkPlaylist()
        if duration > 0:
            if time.time() - timer_start >= duration:
                running = 0
configure()
print(hauntIntervalMin)
print(hauntIntervalMax)
haunt(hauntIntervalMin,hauntIntervalMax)
