#!/usr/bin/python
import pylsdj
import sys
import os.path

# check argv length
if (sys.argv <= 5):
    sys.exit('Usage : python export.py ([SAVEFILE.sav] [#TRACKNUMBER] or [SONGFILE.srm|.lsdsng]) [#SYNTHNUMBER] [SYNTH.snt]')

# get file patcher
savpath = sys.argv[1]
ext = os.path.splitext(savpath)[1]

# check data depending on extension and gather project file
if ext == '.sav':
    # get cmdline args
    synthnumber = int(sys.argv[3])
    synthpath = sys.argv[4]
    # load .sav file
    sav = pylsdj.SAVFile(savpath)
    # get project
    project = sav.projects[int(sys.argv[2])]
elif ext == '.srm' or ext == '.lsdsng':
    # get cmdline args
    synthnumber = int(sys.argv[2])
    synthpath = sys.argv[3]
    # get project
    project = pylsdj.load_srm(savpath) if ext == '.srm' else pylsdj.load_lsdsng(savpath)
else:
    sys.exit('Invalid savefile/songfile (extension ' + ext + ' unsupported).')

# get song
song = project.song
# get synth
synth = song.synths[synthnumber]
# get synth data
synthdata = [list(chunk) for chunk in list(synth.waves)]
# coalesce the numbers
synthdata = [[(chunk[2*i] << 4) + chunk[2*i+1] for i in range(16)] for chunk in synthdata]
# flatte
synthdata = [byte for chunk in synthdata for byte in chunk]

# log 'it's ok'
print "Writing data to " + synthpath + "..."
# open file
fhandle = open(synthpath, "wb")
# write the data to the file
buf = bytearray(synthdata)
fhandle.write(buf)
# close file
fhandle.close()

# log
print "File has been written as " + synthpath + "."
