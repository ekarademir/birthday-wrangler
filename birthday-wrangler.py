import requests
import re
import codecs

def getbdays(month=3, day=6):
    """Exctrects the Births section from the saved page

    Keyword Arguments:
    month -- Month. (default 3 or March)
    day   -- Day. (default 6)
    """

    # Read page contents from file
    file_head = u'./data/data-raw'
    filename = file_head + u'-' + unicode(month) + u'-' + unicode(day) + u'.dat'

    # Read the content in unicode
    f = codecs.open(filename, 'r', 'utf-8')
    r = f.readline()
    f.close()

    # Separate the birth section [everything between span classes of Births and Deaths]
    # Before the regex search clean up the dash
    births_pattern = u'<span class="mw-headline" id="Births">.*<span class="mw-headline" id="Deaths">'
    births_section = re.search(births_pattern, r.replace(u'\u2013', u'-'))

    # After seperating out the births section we can unflatten it again using end tags of li
    births_section = births_section.group()
    births_section = births_section.replace(u'</li>', u'\n')

    # Get all li elements. Later we will clean up these tags.
    items_pattern = u'<li>.*'
    births_items = re.findall(items_pattern, births_section)

    # Clean up the HTML tags
    replace_pattern = u'<.*?>'
    births_items = map(lambda x: re.sub(replace_pattern, u'\x20',x), births_items)

    # Clean up the died year
    replace_pattern = u'\(d.*?\)'
    births_items = map(lambda x: re.sub(replace_pattern, u'\x20',x), births_items)

    # Parse all the lines
    #births_items = map(lambda x: parseline(x, month, day), births_items)

    return births_items

def fetchpage(month=3, day=6):
    """Fetches the wikipedia page for given month and day

    Keyword Arguments:
    month -- Month. (default 3 or March)
    day   -- Day. (default 6)
    """
    file_head = './data/data-raw'
    url_head = 'https://en.wikipedia.org/wiki/'
    months = {
        1 : u'January',
        2 : u'February',
        3 : u'March',
        4 : u'April',
        5 : u'May',
        6 : u'June',
        7 : u'July',
        8 : u'August',
        9 : u'September',
        10 : u'October',
        11 : u'November',
        12 : u'December'
    }

    wikipage = url_head + months[month] + u'_' + unicode(day)
    filename = file_head + u'-' + unicode(month) + u'-' + unicode(day) + u'.dat'

    # Fetch the contents of the date page
    print wikipage.encode('utf-8')
    r = requests.get(wikipage)
    r.encoding = 'utf-8'

    # Open a unicode stream and dump the contents
    f = codecs.open(filename, 'w', 'utf-8')
    f.write(r.text.replace('\n',u'\x20')
                  .replace(u'\u2013', u'-'))
    f.close()

def fetchmonth(month):
    """Fetches mone month from wikipedia

    Arguments
    month -- is an integer value for the month (1 to 12)
    """

    months = [31, 29, 31,   # January, February, March
              30, 31, 20,   # April, May, June
              31, 31, 30,   # July, August, September
              31, 30, 31]   # October, November, December
    days = range(1,months[month-1]+1)

    map(lambda x: fetchpage(month,x), days)

def fetchallpages():
    """Fetches all wikipedia date pages one by one saves them on the disk"""

    months = range(1,13)
    map(fetchmonth, months)

def parseline(line, month, day):
    """Parse the line and return a dictionary for the data.
    line must be a string."""

    # For now lines without proper format are ignored
    if not u',' in line and u'-' in line:
        raise ValueError


    # left from the dash is year
    temp = line.split(u'-')
    year = int(re.search(u'[0-9]+',temp[0]).group())

    # from the remaining, left of FIRST comma is the full name
    #temp = re.sub(temp[1])
    temp = temp[1].strip().split(u',',1)
    fullname = re.findall('\w+',temp[0].strip())
    fullname = u" ".join(fullname)

    # parse the nationality and occupation
    rest = re.findall(u'[A-Za-z]+',temp[1])

    forbidden = [u'and', u'of', u'the', u'with', u'st', u'nd', u'rd', u'th']

    # later on a better way should be implemented
    nationality = [x for x in rest if not x.islower() and not x in forbidden]
    occupation = [x for x in rest if x.islower() and not x in forbidden]

    return {
        'year': year,
        'month': month,
        'day': day,
        'fullname': fullname,
        'nationality': ' '.join(nationality),
        'occupation': occupation
    }

def getallbdays():
    """Reads all the saved files and parses all birthdays. If parsing is
       unsuccessful, writes the line into a file."""

    # Open up the file to write failed lines
    failfile = u'./data-failedlines.dat'
    failedlines = codecs.open(failfile, 'w', 'utf-8')
    fails = 0

    # Open up the file to write csv
    csvfile = u'./data-wikibdays-occupations.csv'
    csvf = codecs.open(csvfile,'w','utf-8')
    successes = 0

    months = [31, 29, 31,   # January, February, March
              30, 31, 20,   # April, May, June
              31, 31, 30,   # July, August, September
              31, 30, 31]   # October, November, December
    #months = [1]

    # This is super inefficient but we don't need concurrency right now
    # Iterate over all files and write the resulting data into a csv files
    # All failed lines are also reported
    for month in range(1, len(months)+1):
        days = range(1,months[month-1]+1)
        for day in days:
            bdays = getbdays(month,day)
            for bday in bdays:
                try:
                    #parseline(bday, month, day)
                    csvf.write(dicttocsv(parseline(bday, month, day)))
                    successes = successes + 1
                except:
                    failedlines.write(bday+u'\n')
                    fl = u"Failed: " + bday
                    print fl.encode('utf-8')
                    fails = fails + 1

    failedlines.close()
    csvf.close()
    print u"Success: {0:d}, Fails: {1:d}, Total: {2:d}".format(successes, fails, successes+fails)

def dicttocsv(d):
    """Converts the bday dict to CSV string"""
    csvstring = u""
    for occ in d['occupation']:
        line = u"{0:d},{1:d},{2:d},{3},{4},{5}\n".format(d['year'],
                                    d['month'],
                                    d['day'],
                                    d['fullname'],
                                    d['nationality'],
                                    occ)
        csvstring = csvstring + line
    return csvstring

if __name__ == "__main__":
    # USE THE SCRIPT BY FOLLOWING HERE
    # Uncomment the following to gather all wikipedia date pages
    #fetchallpages()
    # Uncomment the following line to parse all bdays
    getallbdays()

    #USED FOR DEBUGGING ######################################################
    #bdays = getbdays(3,6)
    #print len(bdays)

    #bi = 20
    #print bdays[bi].strip().encode('utf-8')
    #cform = [hex(ord(x)) + ' ' for x in bdays[bi]]
    #print cform
    #print parseline(bdays[bi], 3, 6)

    #for s in bdays:
    #    print s.strip().encode('utf-8')
    #    try:
    #        parseline(s, 3, 6)
    #    except:
    #        print s.strip().encode('utf-8')
