#!/usr/bin/python
import pylsdj
import sys
import os.path

# check argv length
if (sys.argv <= 5) {
    sys.exit('Usage : python patcher.py ([SAVEFILE.sav] [#TRACKNUMBER] or [SONGFILE.srm|.lsdsng]) [SYNTH.snt] [#SYNTHNUMBER]')
}

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
    synthpath = int(sys.argv[2])
    synthnumber = int(sys.argv[3])
    # get project
    project = pylsdj.load_srm(savpath)
else:
    sys.exit('Invalid savefile/songfile (extension ' + ext + ' unsupported).')

# get song
song = project.song
# get synth
synth = song.synths[synthnumber]
# unlock
synth.wave_synth_overwrite_lock = True

# read bin file
with open(synthpath, 'rb') as f:
    synthdata = f.read()

# chunk synth data
synth.waves = [synthdata[x:x+8] for x in range(0, len(synthdata), 8)]

# save modified file
if ext == '.sav':
    sav.save(savpath)
elif ext == '.srm':
    project.save_srm(savpath)
elif ext == '.lsdsng':
    project.save_lsdsng(savpath)
else:
    sys.exit('Invalid savefile/songfile (extension ' + ext + ' unsupported).')
