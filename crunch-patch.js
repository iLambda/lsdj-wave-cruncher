var fs = require('fs')
var _ = require('lodash')
var path = require('path')
var cruncher = require('./lib/cruncher.js')
var flags = require('flags')
var PythonShell = require('python-shell')


// define flags
flags.defineBoolean('normalize', false, 'Normalize the wave ?')
flags.defineBoolean('cleartemp', true, 'Clear the temporary .snt file ?')
flags.defineInteger('channel', 0, 'Channel for data?')

// check usage
if (process.argv.length < 6) {
  console.log('Usage: node crunch-patcher.js [SOUND.WAV] [NOTE|BASE FREQUENCY] ([SAVEFILE.sav] [#TRACKNUMBER] or [SONGFILE.srm|.lsdsng]) [#SYNTHNUMBER]');
  process.exit(1);
}

// parse flags
flags.parse(process.argv.slice(6))

// log
console.log("Crunching data...")
// crunch
var synthdata = cruncher(process.argv[2], process.argv[3], {
  normalize: flags.get('normalize'),
  channel: flags.get('channel')
})


// log
var filename = path.basename(process.argv[2], path.extname(process.argv[2])) + '.snt.tmp'
console.log("Saving temp data as" + filename + "...")
// creating buffer
var buf = Buffer.from(_.map(_.chunk(synthdata, 2), function (chunk) {
  return _.reduce(chunk, function(cur, oth) {
    return (cur << 4) + oth
  }, 0)
}))

// save buff
filename = path.dirname(process.argv[2]) + "/" + filename
fs.writeFile(filename, buf, function(err) {
  // error
  if (err) {
    console.log("Error : " + err)
    process.exit(1)
  } else {
    console.log("Successfully output " + filename + "!")
  }
})

// create shell
var args = process.argv.slice(4)
args = _.take(args, args.length - 1).concat(filename, _.last(args))
var shell = new PythonShell('./lib/patcher.py', { args: args })

// log msgs
shell.on('message', function (msg) {
  // handle message (a line of text from stdout)
  console.log(msg)
})

// end
shell.end(function (err) {
  // error
  if (err) {
    console.log("Error : " + err)
    process.exit(1)
  }

  // clear temp ?
  if (flags.get('cleartemp')) {
    fs.unlinkSync(filename)
  } else {
    fs.renameSync(filename, filename.slice(0, -3))
  }

  // done
  console.log('Done!')
})
