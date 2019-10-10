import urllib.request
byte_contents = urllib.request.urlopen("https://people.cs.kuleuven.be/~btw/roosters1920/cws_semester_1.html").read()
contents = byte_contents.decode('utf-8')
test = contents.find("<tr><td>")
print(contents[test:test+100])
