import requests
import re

def fetchbdays(month=3, day=6):
    """Fetches the wikipedia page for given month and day

    Keyword Arguments:
    month -- Month. (default 3 or March)
    day   -- Day. (default 6)
    """

    url_head = 'https://en.wikipedia.org/wiki/'
    months = {
        1 : 'January',
        2 : 'February',
        3 : 'March',
        4 : 'April',
        5 : 'May',
        6 : 'June',
        7 : 'July',
        8 : 'August',
        9 : 'September',
        10 : 'October',
        11 : 'November',
        12 : 'December'
    }

    wikipage = url_head + months[month] + '_' + str(day)

    # Fetch the contents of the date page
    r = requests.get(wikipage)

    # Separate the birth section [everything between span classes of Births and Deaths]
    # Before the regex search flatten the content string into one line
    # and clean up the dash
    births_pattern = u'<span class="mw-headline" id="Births">.*<span class="mw-headline" id="Deaths">'
    r.encoding = 'utf-8'
    births_section = re.search(births_pattern, r.text.replace('\n',u'\x20')
                                                .replace(u'\u2013', u'-'))
    #births_section = re.search(births_pattern, r.content.replace('\n','\00'))
                                                #.replace('\xe2\x80\x93','-'))

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

def fetchall(arg):
    pass

def parseline(line, month, day):
    """Parse the line and return a dictionary for the data.
    line must be a string."""

    # For now lines without proper format are ignored
    if not u',' in line and u'-' in line:
        return {}


    # left from the dash is year
    temp = line.split(u'-')
    year = int(re.search(u'[0-9]+',temp[0]).group())

    # from the remaining, left of FIRST comma is the full name
    #temp = re.sub(temp[1])
    temp = temp[1].strip().split(u',',1)
    fullname = temp[0]
    print '"'+fullname+'"'
    fullname = re.search(u'(\w+ )+\w+',temp[0]).group()

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
    bdays = fetchbdays(3,6)
    print len(bdays)

    bi = 0

    print bdays[bi].strip().encode('utf-8')

    cform = [hex(ord(x)) + ' ' for x in bdays[bi]]

    #print cform

    #for s in bdays:
    #    print s.strip().encode('utf-8')

    print parseline(bdays[bi], 3, 6)

    """
    for i in range(len(bdays)):
        try:
            parseline(unicode(bdays[i]), 3, 6)
        except Exception as e:
            print bdays[i]
            print i
            raise
    """
