import requests
r = requests.get('https://en.wikipedia.org/wiki/March_6')

lines = r.content.splitlines()

print len(lines)
