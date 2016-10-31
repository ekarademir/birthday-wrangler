import requests
import re
import codecs

def fetchbdays(month=3, day=6):
    """Fetches the wikipedia page for given month and day

    Keyword Arguments:
    month -- Month. (default 3 or March)
    day   -- Day. (default 6)
    """

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

    wikipage = url_head + months[month] + '_' + unicode(day)

    # Fetch the contents of the date page
    r = requests.get(wikipage)

    # Separate the birth section [everything between span classes of Births and Deaths]
    # Before the regex search flatten the content string into one line
    # and clean up the dash
    births_pattern = u'<span class="mw-headline" id="Births">.*<span class="mw-headline" id="Deaths">'
    r.encoding = 'utf-8'
    births_section = re.search(births_pattern, r.text.replace('\n',u'\x20')
                                                .replace(u'\u2013', u'-'))

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
    f = codecs.open(filename, 'w', 'utf_8')
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
    fullname = re.search(u'(\w+ )+\w+',temp[0].strip()).groups()

    # parse the nationality and occupation
    rest = re.findall(u'[A-Za-z]+',temp[1])

    forbidden = [u'and']

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

if __name__ == "__main__":
    # USE THE SCRIPT BY FOLLOWING HERE
    # Uncomment the following to gather all wikipedia date pages
    #fetchallpages()

    ########################################################
    #bdays = fetchbdays(3,6)
    #print len(bdays)

    #bi = 0
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
