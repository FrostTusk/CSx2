const express = require('express');
const fs = require('fs');
// App
const app = express();

var ical_memory = {};
var ical_memory_time;

function read_in_ical() {
  ical_memory = {};
  var lineReader = require('readline').createInterface({
    input: require('fs').createReadStream('test.ical')
  });
  ical_memory_time = fs.statSync("test.ical").mtime;

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

      if (ical_memory[entry])
        ical_memory[entry].push(buffer);
      else
        ical_memory[entry] = [buffer];

      buffer = [];
    }
  });

  lineReader.on('close', function() {
    console.log(ical_memory)
    console.log("read in ical file");
  });
}

read_in_ical();

function eventListToString(eventList) {
  result = "";
  for (i in eventList) {
    result += eventList[i] + "\r\n"
  }
  return result
}
//parse_ical(file);
//http://localhost:8795/something?color1=red&color2=blue.ical
app.get('/something', (req, res) => {
  var stats = fs.statSync("test.ical");
  var mtime = stats.mtime;
  if (mtime > ical_memory_time) {
    console.log("reading ical in again");
    read_in_ical();
  }

  let result = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-\/\/MCWS Classes\/\/EN\r\n';
  for (param in req.query) {
    console.log(ical_memory[param])
    for (i in ical_memory[param]) {
      result += eventListToString(ical_memory[param][i])
    }
  }

  result += "END:VCALENDAR\r\n\r\n";
  res.setHeader('content-type', 'text/calendar');
  res.set("Content-Disposition", "attachment;filename=events.ical");
  //fs.writeFileSync("synchronous.ical", result);
  //res.sendFile('./synchronous.ical', { root: __dirname });
  res.send(result);
});

app.get('/outlook', (req, res) => {
  var stats = fs.statSync("test.ical");
  var mtime = stats.mtime;
  if (mtime > ical_memory_time) {
    console.log("reading ical in again");
    read_in_ical();
  }

  console.log(req.query);
  let result = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-\/\/MCWS Classes\/\/EN\r\n' +
               'METHOD:PUBLISH\r\nCALSCALE:GREGORIAN\r\nNAME:Events in History\r\nX-WR-CALNAME:Events in History\r\n' +
               'UID:americanhistorycalendar.com-zapcal-8E8F12428D96FDF0-\r\n' +
               'X-WR-RECALID:americanhistorycalendar.com-zapcal-8E8F12428D96FDF0-\r\n' +
               'REFRESH-INTERVAL;VALUE=DURATION:D1D\r\n' +
               'BEGIN:VTIMEZONE\r\n' +
               'TZID:UTC\r\n' +
               'BEGIN:STANDARD\r\n' +
               'DTSTART:20070101T000000\r\n' +
               'TZOFFSETFROM:+0000\r\n' +
               'TZOFFSETTO:+0000\r\n' +
               'TZNAME:UTC\r\n' +
               'END:STANDARD\r\n' +
               'END:VTIMEZONE\r\n'
  for (param in req.query) {
    for (i in ical_memory[param]) {
      result += eventListToString(ical_memory[param][i])
    }
  }

  result += "END:VCALENDAR\r\n\r\n";
  res.setHeader('content-type', 'text/calendar; charset=utf-8');
  res.set("Content-Disposition", 'inline; filename=ical.ics');
  res.set("X-Content-Type-Options", "nosniff");
  res.set("Cache-Control", "must-revalidate");
  res.set("Pragma", "public")
  res.set("Last-Modified", mtime.toString());
  //fs.writeFileSync("synchronous.ical", result);
  //res.sendFile('./synchronous.ical', { root: __dirname });
  res.send(result);
})
//
// app.use(function(req, res, next) {
//   delete req.headers['content-type']; // should be lowercase
//   next();
// });
app.set('etag', false)
app.set('x-powered-by', false);
app.listen(8795, '0.0.0.0');
