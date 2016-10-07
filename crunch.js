var fs = require('fs')
var _ = require('lodash')
var path = require('path')
var wav = require('node-wav')

// check usage
if (process.argv.length < 3) {
  console.log('Usage: node ' + process.argv[1] + ' FILENAME');
  process.exit(1);
}

// get buffer
var filename = process.argv[2]
var buffer = fs.readFileSync(filename, 'utf8')
var data = wav.decode(buffer)
