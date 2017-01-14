var _ = require('lodash')
var fs = require('fs')
var tonal = require('tonal')
var wav = require('node-wav')
var Pitchfinder = require('pitchfinder')

LSDJ = {
  constants: {
    SAMPLES_PER_FRAMES: 32,
    FRAMES_PER_TABLE: 16,
    FRAME_RESOLUTION: 16
  }
}

module.exports = function(wave, note, options) {
  // default options
  options = options || {}
  options = {
    channel: options.channel || 0,
    normalize: options.normalize,
    linear: options.linear,
    exp: options.exp
  }

  // get frequency
  // auto-detect if argument is "auto"
  if (note == "auto") {
  const detectPitch = new Pitchfinder.YIN();
  const freqbuffer = fs.readFileSync(wave);
  const decoded = wav.decode(freqbuffer); // get audio data from file using `wav-decoder` 
  const float32Array = decoded.channelData[0]; // get a single channel of sound 
  note = detectPitch(float32Array); // null if pitch cannot be identified
  // check for null value
    if (!note) {
    throw "Could not auto-detect frequency"
    } else {
    console.log("Frequency detected: " + parseFloat(note) + " Hz")
    }
  }
  
  var freq = parseFloat(note) || tonal.toFreq(note)
  if (note != freq) {
  console.log(note + " equals " + freq + " Hz")
  }
  // check frequency
  if (!freq || !_.isFinite(freq)) {
    throw "Note frequency \"" + note + "\" is invalid."
  }

  // get original wav data
  if (_.isString(wave)) {
    // read file w/ filename
    var buffer = fs.readFileSync(wave)
    // get data
    wave = wav.decode(buffer)
  } else {
    throw "Wav data is not legible."
  }

  // resample
  
  // unused variable
  // var samplingFreq = freq * LSDJ.constants.SAMPLES_PER_FRAMES
  
  var n = LSDJ.constants.SAMPLES_PER_FRAMES * LSDJ.constants.FRAMES_PER_TABLE
  var data = wave.channelData[options.channel]
  
  // check for interpolation
  if (options.linear || options.exp) {
  var cycles = ~~((data.length * freq) / wave.sampleRate)
  var cycleInterval = cycles/LSDJ.constants.FRAMES_PER_TABLE
  console.log('Samples: ' + data.length + '\nSample rate: ' + wave.sampleRate + '\nCycles: ' + cycles)
  var rangeList = []
  var sample = 0
  
  // linear interpolation
    if (options.linear || cycles < 32) {
      if (options.exp) {
        console.log('Sample is too short. Reverting to linear interpolation')
        options.exp = 0
      }
      console.log('Linear interpolation\nTaking frame every ' + ~~(cycleInterval) + ' cycles')
      sample = 0
      for (cycle = 0; cycle < 16; cycle++) {
        sample = ~~(cycleInterval) * cycle * LSDJ.constants.SAMPLES_PER_FRAMES
          for (nextSample=0; nextSample < 32; nextSample++) {
            // console.log(sample)
            rangeList.push(sample)
            sample = sample + 1
          }
      }
      
  // "exponential" interpolation, sort of
    } else if (options.exp) {
        console.log('Exponential interpolation')
        cycle = 0
        cycleLog = Math.pow(Math.E, (Math.log(cycles) / LSDJ.constants.FRAMES_PER_TABLE))
        for (cyc = 0; cyc < 16; cyc++) {
          // console.log('Cycle number ' + (cycle/LSDJ.constants.SAMPLES_PER_FRAMES))
            for (nextSample=0; nextSample < 32; nextSample++) {
              // console.log(cycle)
              rangeList.push(~~(cycle))
              cycle = cycle + 1
            }
          cycle = (Math.round(Math.pow(cycleLog,cyc*1.1)) * LSDJ.constants.SAMPLES_PER_FRAMES) + (cyc * LSDJ.constants.SAMPLES_PER_FRAMES)
      }
    }
    
  // otherwise get all samples from the beginning
  } else {
   var rangeList = _.range(n)
  }
  
  var samples = _.map(rangeList, function (i) {
   // compute adequate time
    var t = (i / (freq * LSDJ.constants.SAMPLES_PER_FRAMES))
    // get sample number in original coordinates
    var j = wave.sampleRate * t
    // get value, return it (interpolated w/ next value, currently disabled)
    return data[~~j]// + ((j - ~~j) * (data[1 + ~~j] || 0))
  })

  // normalize if required
  if (options.normalize) {
    var max = Math.abs(_.maxBy(samples, Math.abs))
    samples = _.map(samples, function (i) { return i / max })
  }

  // bitcrush
  samples = _.map(samples, function(float) {
    return ~~((float + 1.0) * LSDJ.constants.FRAME_RESOLUTION * 0.5)
  })

  // return samples
  return samples
}
