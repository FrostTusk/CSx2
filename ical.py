import urllib.request
import datetime, pytz, sys
import os.path

# --- Constants
TARGET_URL = 'https://people.cs.kuleuven.be/~btw/roosters1920/cws_semester_1.html'
OUT_FILENAME = 'events.ical'
# ---

class Event:
    _set = False

    # Sets all the atributes of the Event
    # and moves the daycursor to the next Event in that day.
    def parse_in_event(self, week, daycursor, date, out):
        if self._set:
            raise ValueError

        time = week[daycursor+8:week.find('</td>',daycursor)]
        starttime = datetime.datetime.strptime(time.split('&#8212;')[0], '%H:%M').time()
        endtime = datetime.datetime.strptime(time.split('&#8212;')[1], '%H:%M').time()

        self.startdt = datetime.datetime.combine(date=date, time=starttime)
        self.enddt = datetime.datetime.combine(date=date, time=endtime)

        local_tz = pytz.timezone('Europe/Brussels')
        self.startdt = local_tz.localize(self.startdt)
        self.enddt = local_tz.localize(self.enddt)

        self.startdt = self.startdt.astimezone(pytz.timezone("utc"))
        self.enddt = self.enddt.astimezone(pytz.timezone("utc"))

        daycursor = week.find('<td>in</td>',daycursor+1)
        self.location = week[daycursor+20:week.find('</td>', daycursor+20)].replace(' '*5,' ')

        daycursor = week.find('>', week.find('<font', daycursor)) + 1
        self.name = week[daycursor:week.find('</font>', daycursor+1)]

        self._set = True
        return week.find('<tr><td>', daycursor + 1)

    def write_to_file(self, out):
        out.write('BEGIN:VEVENT\n')
        out.write('DTSTART:' + str(self.startdt.strftime('%Y%m%dT%H%M%S')) + '\n')
        out.write('DTEND:' + str(self.enddt.strftime('%Y%m%dT%H%M%S')) + '\n')
        out.write('LOCATION:' + self.location + '\n')
        out.write('SUMMARY:' + self.name + '\n')
        out.write('END:VEVENT\n')

def get_date(week):
    date = week[week.find('<b>')+3:week.find('</b>')-5]
    date = date.split(' ')[1].split('.')
    return datetime.date(year=int(date[2]), month=int(date[1]), day=int(date[0]))

def iterate_day(week, date, course_filter, out):
    daycursor = week.find('<tr><td>')
    while(daycursor > 0):
        event = Event()
        daycursor = event.parse_in_event(week, daycursor, date, out)
        if len(course_filter) == 0 or event.name.strip() in course_filter:
            event.write_to_file(out)

def get_course_filter(filename):
    f = open(filename, 'r')
    course_filter = f.readlines()
    f.close()
    for i in range(len(course_filter)):
        course_filter[i] = course_filter[i].strip()
    return course_filter

# python3 ical.py <textfile, EXACT names of courses>
def main():
    course_filter = []
    if len(sys.argv) >= 2 and os.path.isfile(sys.argv[1]):
        course_filter = get_course_filter(sys.argv[1])

    contents = urllib.request.urlopen(TARGET_URL).read().decode('utf-8')
    cursor = contents.find('<hr>') # Skip to first week

    out = open(OUT_FILENAME, 'w+')
    out.write('BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//MCWS Classes//EN\n')

    while(cursor > 0):
        weekend = contents.find('<hr>', cursor+1)
        if weekend == -1:
            weekend = contents.find('<hr color="black" size="4">', cursor+1)

        week = contents[cursor:weekend]

        # iterate over the given day and write to file
        date = get_date(week)
        iterate_day(week, date, course_filter, out)

        cursor = contents.find('<hr>', cursor + 1)

    out.write('END:VCALENDAR\n')
    out.close()

main()
