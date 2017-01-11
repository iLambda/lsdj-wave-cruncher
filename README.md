# lsdj-wave-cruncher

lsdj-wave-cruncher is a bundle of scripts allowing an LSDJ user to create wavetables instruments in LSDJ (a steel drum, or other instruments with complex waveforms).

***WARNING ⚠️*** : *.snt files only contain the 16-frames long 4-bit waveform data. The synth parameters are not saved.*

## crunching

**Crunching** a sample is downsampling and bitcrushing the given sample into a .snt binary file ready to be patched to a LSDJ song.

To *crunch* a sample, use :
```
$ node crunch.js [SAMPLE.WAV] [NOTE|FREQUENCY] --normalize --channel=0
```
* *[SAMPLE.WAV]* is the file that'll be crunched.
* *[NOTE|FREQUENCY|auto]* is either the note at which the sample is (ex: C4, D4), its frequency (ex: 440 Hz), or auto to auto-detect the frequency.
* *--normalize*, if present, will [normalize](https://en.wikipedia.org/wiki/Audio_normalization) the sample.
* *--channel=0* specifies the channel where the sound data will be taken. If not present, it defaults to the 1st channel (0). This parameter is only relevant for stereo sound.


## patching

**Patching** a synth is writing the binary .snt data into a LSDJ song.

To *patch* a synth, you can use both of these commands :
```
$ node patch.js [LSDJSAVE.SAV] [SONGNUMBER] [SYNTHFILE.SNT] [SYNTHNUMBER]
$ node patch.js [SONG.LSDSNG|.SRM] [SYNTHFILE.SNT] [SYNTHNUMBER]
```

* *[LSDJSAVE.SAV]* is the save that'll be patched. If you want to patch a .SAV file, you'll have to supply the number of the song *[SONGNUMBER]* you want to add the synth to.
* *[SONG.LSDSNG|.SRM]* is the song file that'll be patched. In that case, you don't have to supply a song number.
* *[SYNTHFILE.SNT]* is the synth data that'll be patched.
* *[SYNTHNUMBER]* is the ID of the synth where the data will be written.

## crunch-patching

**Crunch-patching** is downsampling and bitcrushing a sample and writing it right away into a LSDJ save file/song.

To *crunch-patch* a sample, you can use both of these commands :
```
$ node crunch-patcher.js [SAMPLE.WAV] [NOTE|FREQUENCY|auto] [LSDJSAVE.SAV] [SONGNUMBER] [SYNTHNUMBER]
$ node crunch-patcher.js [SAMPLE.WAV] [NOTE|FREQUENCY|auto] [SONG.SRM|.LSDSNG] [SYNTHNUMBER]
```

* *[SAMPLE.WAV]* is the file that'll be crunched.
* *[NOTE|FREQUENCY|auto]* is either the note at which the sample is (ex: C4, D4), its frequency (ex: 440 Hz), or auto to auto-detect the frequency.
* *[LSDJSAVE.SAV]* is the save that'll be patched. If you want to patch a .SAV file, you'll have to supply the number of the song *[SONGNUMBER]* you want to add the synth to.
* *[SONG.LSDSNG|.SRM]* is the song file that'll be patched. In that case, you don't have to supply a song number.
* *[SYNTHNUMBER]* is the ID of the synth where the data will be written.


## exporting

**Exporting** a synth is extracting synth data from an existing LSDJ save or song and exporting it as a .snt file.

To *export* a synth, you can use both of these commands :
```
$ node export.js [LSDJSAVE.SAV] [SONGNUMBER] [SYNTHFILE.SNT] [SYNTHNUMBER]
$ node export.js [SONG.LSDSNG|.SRM] [SYNTHFILE.SNT] [SYNTHNUMBER]
```

* *[LSDJSAVE.SAV]* is the save that'll be used as source. If you want to find a synth in a .SAV file, you have to supply the number of the song *[SONGNUMBER]* you'll want to get the synth from.
* *[SONG.LSDSNG|.SRM]* is the song file that'll be used as source. In that case, you don't have to supply a song number.
* *[SYNTHFILE.SNT]* is the path of the .snt file that'll be created.
* *[SYNTHNUMBER]* is the ID of the synth that'll be exported.
