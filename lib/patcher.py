#!/usr/bin/python
import pylsdj
import sys
import os.path

# check argv length
if (len(sys.argv) < 4):
    sys.exit('Usage : python patcher.py ([SAVEFILE.sav] [#TRACKNUMBER] or [SONGFILE.srm|.lsdsng]) [SYNTH.snt] [#SYNTHNUMBER]')

# get file patcher
savpath = sys.argv[1]
ext = os.path.splitext(savpath)[1]

# check data depending on extension and gather project file
if ext == '.sav':
    # get cmdline args
    synthpath = sys.argv[3]
    synthnumber = int(sys.argv[4])
    # load .sav file
    sav = pylsdj.SAVFile(savpath)
    # get project
    project = sav.projects[int(sys.argv[2])]
elif ext == '.srm' or ext == '.lsdsng':
    # get cmdline args
    synthpath = sys.argv[2]
    synthnumber = int(sys.argv[3])
    # get project
    project = pylsdj.load_srm(savpath) if ext == '.srm' else pylsdj.load_lsdsng(savpath)
else:
    sys.exit('Invalid savefile/songfile (extension ' + ext + ' unsupported).')

# get song
song = project.song
# get synth
synth = song.synths[synthnumber]

# read bin file
with open(synthpath, 'rb') as f:
    synthdata = f.read()

# chunk synth data
synthdata = [synthdata[x:x+16] for x in range(0, len(synthdata), 16)]
for i in range(len(synthdata)):
    for j in range(len(synthdata[i])):
        try:
             synth.waves[i][2*j] = ord(synthdata[i][j]) >> 4
        except:
             synth.waves[i][2*j] = synthdata[i][j] >> 4
        try:
             synth.waves[i][2*j+1] = ord(synthdata[i][j]) & 0x0F
        except:
             synth.waves[i][2*j+1] = synthdata[i][j] & 0x0F

# save modified file
if ext == '.sav':
    sav.save(savpath)
    print(savpath + ' saved!')
elif ext == '.srm':
    project.save_srm(savpath)
    print(savpath + ' saved!')
elif ext == '.lsdsng':
    project.save_lsdsng(savpath)
    print(savpath + ' saved!')
else:
    sys.exit('Invalid savefile/songfile (extension ' + ext + ' unsupported).')
