var _ = require('lodash')
var fs = require('fs')
var tonal = require('tonal')
var wav = require('node-wav')

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
  var freq = parseFloat(note) || tonal.toFreq(note)
  // check frequency
  if (!freq || !_.isFinite(freq)) {
    throw "Note frequency is invalid."
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
