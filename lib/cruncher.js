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
    normalize: options.normalize
  }

  // get frequency
  // auto-detect if argument is "auto"
  if (note == "auto") {
  console.log("Auto-detecting frequency...")
  const detectPitch = new Pitchfinder.YIN();
  const buffer = fs.readFileSync(wave);
  const decoded = wav.decode(buffer); // get audio data from file using `wav-decoder` 
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
  console.log(note + " equals " + freq + " Hz")
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
  var samplingFreq = freq * LSDJ.constants.SAMPLES_PER_FRAMES
  var n = LSDJ.constants.SAMPLES_PER_FRAMES * LSDJ.constants.FRAMES_PER_TABLE
  var data = wave.channelData[options.channel]
  var samples = _.map(_.range(n), function (i) {
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
