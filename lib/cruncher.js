var _ = require('lodash')
var tonal = require('tonal')
var wav = require('node-wav')

module.exports = function(wav, note) {
  // get frequency
  var freq = parseFloat(note) || tonal.toFreq(note)
  // check frequency
  if (!freq || !_.isFinite(freq)) {
    throw "Note frequency is invalid."
  }

  // get original wav data
  if (_.isString(wav)) {
    // read file w/ filename
    var buffer = fs.readFileSync(wav)
    // get data
    wav = wav.decode(buffer)
  } else if (_.isArray(wav)){
    // filter array of samples
  } else {
    throw "Wav data is not legible."
  }

  // resample

  // bitcrush

  // print wav data
  console.log(wav)
}
