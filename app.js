const express = require('express');
const fs = require('fs');
// App
const app = express();

let ical_memory = {};
let ical_memory_time;

function read_in_ical() {
  var lineReader = require('readline').createInterface({
    input: require('fs').createReadStream('events.ical')
  });
  ical_memory_time = fs.statSync("events.ical").mtime;

  let buffer = [];
  lineReader.on('line', function (line) {
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
        ical_memory[entry] = [];

      buffer = [];
    }
  });

  lineReader.on('close', function() {
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
  var stats = fs.statSync("events.ical");
  var mtime = stats.mtime;
  if (mtime > ical_memory_time) {
    console.log("reading ical in again");
    read_in_ical();
  }

  let result = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-\/\/MCWS Classes\/\/EN\r\n';
  for (param in req.query) {
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
})
//
// app.use(function(req, res, next) {
//   delete req.headers['content-type']; // should be lowercase
//   next();
// });
app.set('x-powered-by', false);
app.listen(8795, '0.0.0.0');
