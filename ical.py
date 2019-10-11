import urllib.request
import datetime, pytz, sys
import os.path

# --- Constants
TARGET_URL = 'https://people.cs.kuleuven.be/~btw/roosters1920/cws_semester_1.html'
OUT_FILENAME = 'events.ical'
LOCAL_TIMEZONE = pytz.timezone('Europe/Brussels')
# ---


class Event:
    def __init__(self, to_utc, out):
        self.to_utc = to_utc
        self.out = out
        self._set = False


    # Sets all the attributes of this event.
    # Parses the information from a day_contents string
    # and adjust the day_cursor to the next event.
    # Can only be called once.
    def parse_in_event(self, day_contents, day_cursor, date):
        if self._set:
            raise ValueError

        # Parse the times
        time = day_contents[day_cursor+8:day_contents.find('</td>',day_cursor)]
        starttime = datetime.datetime.strptime(time.split('&#8212;')[0], '%H:%M').time()
        endtime = datetime.datetime.strptime(time.split('&#8212;')[1], '%H:%M').time()

        # Convert the times to datetime objects and localize the timezones
        self.startdt = datetime.datetime.combine(date=date, time=starttime)
        self.startdt = LOCAL_TIMEZONE.localize(self.startdt)
        self.enddt = datetime.datetime.combine(date=date, time=endtime)
        self.enddt = LOCAL_TIMEZONE.localize(self.enddt)

        # Convert to utc
        if self.to_utc:
            self.startdt = self.startdt.astimezone(pytz.timezone("utc"))
            self.enddt = self.enddt.astimezone(pytz.timezone("utc"))

        # Get the location
        daycursor = day_contents.find('<td>in</td>',day_cursor+1)
        self.location = day_contents[day_cursor+20:day_contents.find('</td>', day_cursor+20)].replace(' '*5,' ')

        # Get the name
        day_cursor = day_contents.find('>', day_contents.find('<font', day_cursor)) + 1
        self.name = day_contents[day_cursor:day_contents.find('</font>', day_cursor+1)]

        self._set = True
        return day_contents.find('<tr><td>', day_cursor + 1)


    # Writes the attributes of this event to the event's outputstream.
    def write_event_to_out(self):
        if not self._set:
            raise ValueError

        self.out.write('BEGIN:VEVENT\n')
        self.out.write('DTSTART:' + str(self.startdt.strftime('%Y%m%dT%H%M%S')) + '\n')
        self.out.write('DTEND:' + str(self.enddt.strftime('%Y%m%dT%H%M%S')) + '\n')
        self.out.write('LOCATION:' + self.location + '\n')
        self.out.write('SUMMARY:' + self.name + '\n')
        self.out.write('END:VEVENT\n')


def get_course_filter(filename):
    f = open(filename, 'r')
    course_filter = f.readlines()
    f.close()
    for i in range(len(course_filter)):
        course_filter[i] = course_filter[i].strip()
    return course_filter


def get_date(week):
    date = week[week.find('<b>')+3:week.find('</b>')-5]
    date = date.split(' ')[1].split('.')
    return datetime.date(year=int(date[2]), month=int(date[1]), day=int(date[0]))


def write_day_events_to_out(day_contents, course_filter, out):
    date = get_date(day_contents)

    day_cursor = day_contents.find('<tr><td>')
    while(day_cursor > 0):
        event = Event(True, out)
        day_cursor = event.parse_in_event(day_contents, day_cursor, date)

        if len(course_filter) == 0 or event.name.strip() in course_filter:
            event.write_event_to_out()


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
        next_day_cursor = contents.find('<hr>', cursor+1)
        if next_day_cursor == -1: # Catch edge case at the end of file
            next_day_cursor = contents.find('<hr color="black" size="4">', cursor+1)

        day_contents = contents[cursor:next_day_cursor]
        write_day_events_to_out(day_contents, course_filter, out)

        cursor = contents.find('<hr>', cursor + 1)

    out.write('END:VCALENDAR\n')
    out.close()

main()
