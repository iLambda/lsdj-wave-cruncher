var fs = require('fs')
var _ = require('lodash')
var path = require('path')
var PythonShell = require('python-shell')

// check usage
if (process.argv.length < 5) {
  console.log('Usage: node export.js ([SAVEFILE.sav] [#TRACKNUMBER] or [SONGFILE.srm|.lsdsng]) [#SYNTHNUMBER] [SYNTH.snt]')
  process.exit(1)
}

// create shell
var shell = new PythonShell('./lib/exporter.py', { args: process.argv.slice(2) })

// log msgs
shell.on('message', function (msg) {
  // handle message (a line of text from stdout)
  console.log(msg)
})

// end
shell.end(function (err) {
  // error
  if (err) throw err
  // done
  console.log('Done!')
})
