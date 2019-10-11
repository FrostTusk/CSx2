import urllib.request
import datetime, pytz, sys
import os.path

# --- Constants
TARGET_URL = 'https://people.cs.kuleuven.be/~btw/roosters1920/cws_semester_1.html'
OUT_FILENAME = 'events.ical'
# ---

# python3 ical.py <textfile, EXACT names of courses>
filter = []
if len(sys.argv) == 2 and os.path.isfile(sys.argv[0]):
    f = open(sys.argv[1], 'r')
    filter = f.readlines()
    f.close()

for i in range(len(filter)):
    filter[i] = filter[i].strip()


byte_contents = urllib.request.urlopen(TARGET_URL).read()
contents = byte_contents.decode('utf-8')
cursor = contents.find('<hr>') # Skip to first week

out = open(OUT_FILENAME, 'w+')
out.write('BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//MCWS Classes//EN\n')

def get_date(week):
    date = week[week.find('<b>')+3:week.find('</b>')-5]
    date = date.split(' ')[1].split('.')
    return datetime.date(year=int(date[2]), month=int(date[1]), day=int(date[0]))


class Event:
    # Sets all the atributes of the Event
    # and moves the daycursor to the next Event in that day.
    def parse_in_event(self, week, daycursor):
        time = week[daycursor+8:week.find('</td>',daycursor)]
        starttime = datetime.datetime.strptime(time.split('&#8212;')[0], '%H:%M').time()
        endtime = datetime.datetime.strptime(time.split('&#8212;')[1], '%H:%M').time()

        self.startdt = datetime.datetime.combine(date=date, time=starttime, tzinfo=pytz.timezone('Europe/Brussels'))
        self.enddt = datetime.datetime.combine(date=date, time=endtime, tzinfo=pytz.timezone('Europe/Brussels'))

        daycursor = week.find('<td>in</td>',daycursor+1)
        self.location = week[daycursor+20:week.find('</td>', daycursor+20)].replace(' '*5,' ')

        daycursor = week.find('>', week.find('<font', daycursor)) + 1
        self.name = week[daycursor:week.find('</font>', daycursor+1)]
        return week.find('<tr><td>', daycursor + 1)

    def write_to_file(self, out):
        out.write('BEGIN:VEVENT\n')
        out.write('DTSTART:' + str(self.startdt.strftime('%Y%m%dT%H%M%S')) + '\n')
        out.write('DTEND:' + str(self.enddt.strftime('%Y%m%dT%H%M%S')) + '\n')
        out.write('LOCATION:' + self.location + '\n')
        out.write('SUMMARY:' + self.name + '\n')
        out.write('END:VEVENT\n')


while(cursor > 0):
    weekstart = cursor
    weekend = contents.find('<hr>', cursor+1)
    if weekend == -1:
        weekend = contents.find('<hr color="black" size="4">', cursor+1)

    week = contents[weekstart:weekend]

    date = get_date(week)

    #while for classes
    daycursor = week.find('<tr><td>')
    while(daycursor > 0):
        event = Event()
        daycursor = event.parse_in_event(week, daycursor)
        if len(filter) == 0 or name.strip() in filter:
            event.write_to_file(out)

    cursor = contents.find('<hr>', cursor + 1)



out.write('END:VCALENDAR\n')
out.close()
