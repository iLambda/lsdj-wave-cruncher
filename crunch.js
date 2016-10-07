var fs = require('fs')
var _ = require('lodash')
var path = require('path')
var cruncher = require('./lib/cruncher.js')

// check usage
if (process.argv.length != 4) {
  console.log('Usage: node crunch.js [FILENAME] [NOTE|BASE FREQUENCY]');
  process.exit(1);
}

// crunch
cruncher(process.argv[2], process.argv[3])
