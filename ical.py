import urllib.request
import datetime, pytz

byte_contents = urllib.request.urlopen("https://people.cs.kuleuven.be/~btw/roosters1920/cws_semester_1.html").read()
contents = byte_contents.decode('utf-8')

cursor = contents.find('<hr>')

out = open('events.ics', 'w+')
out.write('BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//MCWS Classes//EN\n')

while(cursor > 0):
    weekstart = cursor
    weekend = contents.find('<hr>', cursor+1)
    if weekend == -1:
        weekend = contents.find('<hr color="black" size="4">', cursor+1)

    week = contents[weekstart:weekend]

    # get the date
    date = week[week.find('<b>')+3:week.find('</b>')-5]
    date = date.split(' ')[1].split('.')
    date = datetime.date(year=int(date[2]), month=int(date[1]), day=int(date[0]))

    #while for classes
    daycursor = week.find('<tr><td>')
    while(daycursor > 0):
        out.write('BEGIN:VEVENT\n')
        time = week[daycursor+8:week.find('</td>',daycursor)]
        starttime = datetime.datetime.strptime(time.split('&#8212;')[0], '%H:%M').time()
        endtime = datetime.datetime.strptime(time.split('&#8212;')[1], '%H:%M').time()

        startdt = datetime.datetime.combine(date=date, time=starttime, tzinfo=pytz.timezone('Europe/Brussels'))
        enddt = datetime.datetime.combine(date=date, time=endtime, tzinfo=pytz.timezone('Europe/Brussels'))

        out.write('DTSTART:' + str(startdt.strftime('%Y%m%dT%H%M%S')) + '\n')
        out.write('DTEND:' + str(enddt.strftime('%Y%m%dT%H%M%S')) + '\n')

        daycursor = week.find('<td>in</td>',daycursor+1)
        out.write(('LOCATION:'+ week[daycursor+20:week.find('</td>', daycursor+20)] + '\n').replace(' '*5,' '))

        daycursor = week.find('>', week.find('<font', daycursor)) + 1
        out.write('SUMMARY:' + week[daycursor:week.find('</font>', daycursor+1)] + '\n')
        out.write('END:VEVENT\n')

        daycursor = week.find('<tr><td>', daycursor + 1)

    cursor = contents.find('<hr>', cursor + 1)



out.write('END:VCALENDAR\n')
out.close()

print(datetime.datetime.utcnow().astimezone(pytz.timezone('Europe/Brussels')))
print((datetime.datetime.utcnow() + datetime.timedelta(days=30)).astimezone(pytz.timezone('Europe/Brussels')))