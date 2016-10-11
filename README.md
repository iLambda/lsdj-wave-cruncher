# lsdj-wave-cruncher

lsdj-wave-cruncher is a bundle of scripts allowing an LSDJ user to create wavetables instruments in LSDJ (a steel drum, or other instruments with complex waveforms).

## crunching

**Crunching** a sample is downsampling and bitcrushing the given sample into a .snt binary file ready to be patched to a LSDJ song.

To *crunch* a sample, use :
```bash
$ node crunch.js [SAMPLE.WAV] [NOTE|FREQUENCY]
```
* [SAMPLE.WAV] is the fine that'll be crunched
* [NOTE|FREQUENCY] is either the note at which the sample is (ex: C4, D4) or its frequency (ex: 440 Hz).

## patching

**Patching** a synth is wrinting the binary .snt data to a LSDJ song.

To *patch* a synth, use :
```bash
$ node patch.js [LSDJSAVE.SAV] [SONGNUMBER] [SYNTHFILE.SNT] [SYNTHNUMBER]
```
or
```bash
$ node patch.js [SONG.LSDSNG|.SRM] [SYNTHFILE.SNT] [SYNTHNUMBER]
```

* *[LSDJSAVE.SAV]* is the save that'll be patched. If you want to patch a .SAV file, you have to supply the number of the song [SONGNUMBER] you'll want to add the synth to.
* *[SONG.LSDSNG|.SRM]* is the song file that'll be patched. In that case, you don't have to supply a song number.
* *[SYNTHFILE.SNT]* is the synth data that'll be patched.
* *[SYNTHNUMBER]* is the ID of the synth that'll be written to.

## crunch-patching

## exporting
