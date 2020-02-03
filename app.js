// ---
// Import
// ---

const trackedFile = "test.ical";
const fs = require('fs');
const moment = require('moment');

let icalMemory = {};
let icalMemoryTime;
let backlog = [];


function importingTrackedFile() {
  console.log("Started importing ical file: " + trackedFile);
  icalMemory = {};
  var lineReader = require('readline').createInterface({
    input: fs.createReadStream(trackedFile)
  });
  icalMemoryTime = fs.statSync(trackedFile).mtime;

  let buffer = [];
  lineReader.on('line', function (line) {
    if (line.indexOf("BEGIN:VCALENDAR") == -1 || line.indexOf("VERSION:2.0") == -1 ||
        line.indexOf("PRODID:") == -1)
        buffer.push(line);
    if (line.indexOf("END:VEVENT") != -1) {
      let entry;
      for (i in buffer) {
        if (buffer[i].indexOf("SUMMARY:") != -1) {
          cursor = buffer[i].indexOf("SUMMARY:") + "SUMMARY:".length;
          entry = buffer[i].slice(cursor).trim();
          break;
        }
      }

      if (icalMemory[entry])
        icalMemory[entry].push(buffer);
      else
        icalMemory[entry] = [buffer];

      buffer = [];
    }
  });

  lineReader.on('close', function() {
    for (i in backlog)
      backlog[i]()
    backlog = [];
    console.log("Finished importing ical file: " + trackedFile);
  });
}

// Load in the initial file
importingTrackedFile();

// ---
// Helper
// ---

function eventListToString(eventList) {
  result = "";
  for (i in eventList) {
    result += eventList[i] + "\r\n"
  }
  return result
}

// ---
// Network
// ---

const express = require('express');
const app = express();
app.set('x-powered-by', false);

function returnGoogleiCal(req, res) {
  let result = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-\/\/MCWS Classes\/\/EN\r\n';
  for (param in req.query) {
    for (i in icalMemory[param]) {
      result += eventListToString(icalMemory[param][i])
    }
  }

  result += "END:VCALENDAR\r\n\r\n";
  res.setHeader('content-type', 'text/calendar');
  res.set("Content-Disposition", "attachment;filename=events.ical");
  res.send(result);
}

/**
 * Endpoint that will serve the tracked file as a calendar.
 * Link should be formed as http:/xxxx/google?xxxxx&...&xxxx.ical
 */
app.get('/google', async function (req, res) {
  console.log("Received /google ical request")
  var stats = fs.statSync(trackedFile);
  var mtime = stats.mtime;
  if (mtime > icalMemoryTime) {
    console.log("Memory ical outdated, re-importing ical file: " + trackedFile);
    backlog.push(function() {returnGoogleiCal(req, res)});
    importingTrackedFile();
  } else {
    returnGoogleiCal(req, res);
  }
});


app.listen(8795, '0.0.0.0');
