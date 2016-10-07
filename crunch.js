var fs = require('fs')
var _ = require('lodash')
var path = require('path')

// check for a filename
if (process.argv.length < 3) {
  console.log('Usage: node ' + process.argv[1] + ' FILENAME');
  process.exit(1);
}

// get filename
var filename = process.argv[2]
var folder = path.dirname(fs.realpathSync(filename, [])) + "/" + path.basename(fs.realpathSync(filename, []).replace(/\./, "_"))
// read sync
data = fs.readFileSync(filename, 'utf8')
