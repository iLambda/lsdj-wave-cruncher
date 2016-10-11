# lsdj-wave-cruncher

lsdj-wave-cruncher is a bundle of scripts allowing an LSDJ user to create wavetables instruments in LSDJ (a steel drum, or other instruments with complex waveforms).

***WARNING ⚠️*** : *.snt files only contain the 16-frames long 4-bit waveform data. The synth parameters are not saved.*

## crunching

**Crunching** a sample is downsampling and bitcrushing the given sample into a .snt binary file ready to be patched to a LSDJ song.

To *crunch* a sample, use :
```
$ node crunch.js [SAMPLE.WAV] [NOTE|FREQUENCY]
```
* [SAMPLE.WAV] is the fine that'll be crunched
* [NOTE|FREQUENCY] is either the note at which the sample is (ex: C4, D4) or its frequency (ex: 440 Hz).

## patching

**Patching** a synth is writing the binary .snt data to a LSDJ song.

To *patch* a synth, you can use both of these commands :
```
$ node patch.js [LSDJSAVE.SAV] [SONGNUMBER] [SYNTHFILE.SNT] [SYNTHNUMBER]
```
```
$ node patch.js [SONG.LSDSNG|.SRM] [SYNTHFILE.SNT] [SYNTHNUMBER]
```

* *[LSDJSAVE.SAV]* is the save that'll be patched. If you want to patch a .SAV file, you have to supply the number of the song [SONGNUMBER] you'll want to add the synth to.
* *[SONG.LSDSNG|.SRM]* is the song file that'll be patched. In that case, you don't have to supply a song number.
* *[SYNTHFILE.SNT]* is the synth data that'll be patched.
* *[SYNTHNUMBER]* is the ID of the synth that'll be written to.

## crunch-patching

## exporting

**Exporting** a synth is extracting synth data from an existing LSDJ save or song and exporting it as a .snt file.

To *export* a synth, you can use both of these commands :
```
$ node export.js [LSDJSAVE.SAV] [SONGNUMBER] [SYNTHFILE.SNT] [SYNTHNUMBER]
```
```
$ node export.js [SONG.LSDSNG|.SRM] [SYNTHFILE.SNT] [SYNTHNUMBER]
```

* *[LSDJSAVE.SAV]* is the save that'll be used as source. If you want to find a synth in a .SAV file, you have to supply the number of the song [SONGNUMBER] you'll want to get the synth from.
* *[SONG.LSDSNG|.SRM]* is the song file that'll be used as source. In that case, you don't have to supply a song number.
* *[SYNTHFILE.SNT]* is the path of the .snt file that'll be created.
* *[SYNTHNUMBER]* is the ID of the synth that'll be exported.
