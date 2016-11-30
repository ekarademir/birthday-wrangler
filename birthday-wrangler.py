import requests, re, codecs, pickle
import numpy as np
from functools import reduce

def getbdays(month=3, day=6):
    """Exctrats the Births section from the saved page

    Keyword Arguments:
    month -- Month. (default 3 or March)
    day   -- Day. (default 6)
    """

    # Read page contents from file
    file_head = u'./data/data-raw'
    filename = file_head + u'-' + str(month) + u'-' + str(day) + u'.dat'

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

    bi = []
    replace_pattern1 = '<.*?>'
    replace_pattern2 = u'\(d.*?\)'
    for birth_item in births_items:
        # Clean up the HTML tags
        t = re.sub(replace_pattern1, u'',birth_item)
        # Clean up the died year
        t = re.sub(replace_pattern2, u'',t)
        bi.append(t)


    return list(bi)

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

    print("Fetching Wiki Month {0} Day {1}".format(month, day))

    wikipage = url_head + months[month] + u'_' + str(day)
    filename = file_head + u'-' + str(month) + u'-' + str(day) + u'.dat'

    # Fetch the contents of the date page
    print(wikipage.encode('utf-8'))
    r = requests.get(wikipage)
    r.encoding = 'utf-8'

    # Open a unicode stream and dump the contents
    f = codecs.open(filename, 'w', 'utf-8')
    f.write(r.text.replace('\n',u'\x20')
                  .replace(u'\u2013', u'-'))
    f.close()

def fetchmonth(month):
    """Fetches one month from wikipedia

    Arguments
    month -- is an integer value for the month (1 to 12)
    """

    months = [31, 29, 31,   # January, February, March
              30, 31, 20,   # April, May, June
              31, 31, 30,   # July, August, September
              31, 30, 31]   # October, November, December
    days = range(1,months[month-1]+1)

    print("Fetching Wiki Month {0}".format(month))
    # map(lambda x: fetchpage(month,x), days)
    for day in days:
        fetchpage(month,day)

def fetchallpages():
    """Fetches all wikipedia date pages one by one saves them on the disk"""

    months = range(1,13)
    print("Fetching Wiki Pages")
    for month in months:
        fetchmonth(month)
    # map(fetchmonth, months)

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

def guess_nationality(test):
    """Guess the unknown nationality with a trained Support Vector Machine"""

    # SVM is trained with words longer than 3 letters
    if len(test) < 3:
        return False

    # We have a list of false positives.
    false_positives = ["politician", "comedian", "magician", "musician",
                       "pakistan", "eli", "hasan"]

    # ending with -an is false positive
    if test[-2:] == "an":
        return False

    if test in false_positives:
        return False

    with open("NationalityDetectorSVM.pickle", mode='rb') as f:
        clf = pickle.load(f)

    X = np.zeros( ( 1, 3 ), dtype = np.int16 )
    X[0, 0:3] = np.array( [ord(x) for x in test[-3:]] )

    return bool(clf.predict(X))

def is_nationality(test):
    """Test if a word is a nationality adjective"""

    with codecs.open("nationalities.txt", "r", "utf-8") as f:
        nationalities = list(map(lambda x: x.strip().lower().split(',')[0], f.readlines()))

    # First check the list. If not guess.
    if test in nationalities:
        return True
    else:
        return False#guess_nationality(test)

def get_nation(nationality):
    """Test id a word is a nationality adjective"""

    with codecs.open("nationalities.txt", "r", "utf-8") as f:
        nationalities = {}
        for x in f.readlines():
            nationalities[x.strip().lower().split(',')[0]] = x.strip().lower().split(',')[1]

    result = nationality[:-2]
    for key,val in nationalities.items():
        if nationality == key:
            result = val

    return result

def get_nationality(nation):
    """Test id a word is a nationality adjective"""

    with codecs.open("nationalities.txt", "r", "utf-8") as f:
        nationalities = {}
        for x in f.readlines():
            nationalities[x.strip().lower().split(',')[1]] = x.strip().lower().split(',')[0]

    result = nation
    for key,val in nationalities.items():
        if nation == key:
            result = val

    return result

def occupations(occupationpart):
    """Parses occupations"""

    # clean up paranthesis parts
    occupationpart = re.sub('\(.+?\)', '', occupationpart)

    # first split by "and" this will sort out: a,b, and c
    occlist = [x.strip() for x in occupationpart.split("and")]

    # then split from comma and combine everything
    occlist = list(reduce(lambda a,x: a + x.split(","), occlist, []))

    # finally clean up empty list items and strip the end spaces
    occlist = list(map(lambda x: x.strip(), filter(lambda x: x != '', occlist)))

    return occlist


def parse_name_nationality_occupation(rest):

    twowordnats = {
                    "cape verdean":"cape_verdean",
                    "central african": "central_african",
                    "east timorese": "east_timorese",
                    "equatorial guinean": "equatorial_guinean",
                    "new zealander": "new_zealander",
                    "new zealand": "new_zealand",
                    "north korean": "north_korean",
                    "south korean": "south_korean",
                    "northern irish": "northern_irish",
                    "south african": "south_african",
                    "sri lankan": "sri_lankan",
                    "hong kong": "hong_kong",
                    "saint lucian": "saint_lucian",
                    "costa rican": "costa_rican",
                    "guinea bissauan": "guinea_bissauan",
                    "papua new guinean": "papua_new_guinean",
                    "san marinese": "san_marinese",
                    "sierra_leonean": "sierra_leonean",
                  }

    for key, value in twowordnats.items():
        rest = rest.replace(key, value)
    # print(rest)
    tokens = rest.split(' ')
    tokens = list(reduce(lambda a,x: a + x.split('-'), tokens, []))
    #test for nationality
    nats = [is_nationality(x) for x in tokens]
    # print(nats)
    # find the order of the first nationality token
    natindex = -1
    natcount = 0
    for i in range(len(nats)):
        if nats[i]:
            natindex = i
            natcount = natcount + 1
        # handle double nationality
        if natcount == 2:
            break

    # if no nationality found return None
    if natindex == -1:
        return rest, None, None, None

    # if singl e nationality, then behave as normal return the expected list
    if natcount == 1:
        nationality = tokens[natindex]
        # where is the nationality in the text?
        natindex = rest.find(nationality)

        # everything before nationality as name, after as occupation
        name = re.sub(',', '', rest[:natindex]).strip()
        occupation = rest[(natindex + len(nationality)):].strip()
        return name, nationality, False, occupations(occupation)

    # if double nationality, then re hyphen the nationality
    elif natcount == 2:
        # print("Double")
        natindex = natindex - 1
        nationality = "-".join(tokens[natindex:natindex+2])
        natindex = rest.find(nationality)
        name = re.sub(',', '', rest[:natindex]).strip()
        occupation = rest[(natindex + len(nationality)):].strip()
        return name, nationality, True, occupations(occupation)
    else:
        return rest, None, None, None

def parseline_ml(line, month, day):
    """Parse the line and return a dictionary for the data.
    line must be a string."""

    # print(line)

    # For now lines without proper format are ignored
    if not u'-' in line:
        raise ValueError

    # line = re.sub(',', '', line)

    # Split from date dash
    line = [k.strip().lower() for k in line.split(u'-',1)]

    year = line[0]

    # Handle BC
    year = year.lower()
    if 'bc' in year:
        year = -1*int(year.replace('bc','').strip())
    else:
        year = int(year)

    fullname, nationality, double_nationality, occupation = parse_name_nationality_occupation(line[1])

    # print(nationality)
    # handle royalty
    if nationality == None:
        if 'of' in fullname:
            fn = fullname.split('of')
            fullname = fn[0].strip()
            nation = fn[1].strip()
            return {
                'year': year,
                'month': month,
                'day': day,
                'fullname': fullname,
                'nationality': get_nationality(nation.strip()),
                'nation': nation,
                'double_nationality': False,
                'occupation': ["royalty"]
            }
        else:
            return {
                'year': year,
                'month': month,
                'day': day,
                'fullname': fullname,
                'nationality': "world citizen",
                'nation': "world",
                'double_nationality': False,
                'occupation': ["royalty"]
            }

    return {
        'year': year,
        'month': month,
        'day': day,
        'fullname': fullname,
        'nationality': nationality,
        'nation': get_nation(nationality.strip()),
        'double_nationality': double_nationality,
        'occupation': occupation
    }
    # return parse_name_nationality_occupation(line[1])

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
    csvf.write(u'i_year,i_month,i_day,s_fullname,s_nationality,s_occupation\n')
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
                    print(fl.encode('utf-8'))
                    fails = fails + 1

    failedlines.close()
    csvf.close()
    print(u"Success: {0:d}, Fails: {1:d}, Total: {2:d}".format(successes, fails, successes+fails))

def getallbdays_ml():
    """Reads all the saved files and parses all birthdays. If parsing is
       unsuccessful, writes the line into a file."""

    # Open up the file to write failed lines
    failfile = u'./data-failedlines-v2.dat'
    failedlines = codecs.open(failfile, 'w', 'utf-8')
    fails = 0

    # Open up the file to write csv
    csvfile = u'./data-wikibdays-occupations-v2.csv'
    csvf = codecs.open(csvfile,'w','utf-8')
    csvf.write(u'i_year,i_month,i_day,s_fullname,s_nationality,b_double_nationality,s_occupation\n')
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
                    # parseline_ml(bday, month, day)
                    csvf.write(dicttocsv_ml(parseline_ml(bday, month, day)))
                    successes = successes + 1
                except TypeError:
                    failedlines.write(bday+' None TypeError'+u'\n')
                    fl = u"Failed: " + bday
                    print(fl.encode('utf-8'), 'Type Error')
                    fails = fails + 1
                except ValueError:
                    failedlines.write(bday+' ValueError'+u'\n')
                    fl = u"Failed: " + bday
                    print(fl.encode('utf-8'), 'Value Error')
                    fails = fails + 1
                except:
                    failedlines.write(bday+' Unknown Error'+u'\n')
                    fl = u"Failed: " + bday
                    print(fl.encode('utf-8'), 'Unknown Error')
                    fails = fails + 1

    failedlines.close()
    csvf.close()
    print(u"Success: {0:d}, Fails: {1:d}, Total: {2:d}".format(successes, fails, successes+fails))

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

def dicttocsv_ml(d):
    """Converts the bday dict to CSV string"""
    csvstring = u""
    for occ in d['occupation']:
        line = u"{0:d},{1:d},{2:d},{3},{4},{5:d},{6}\n".format(d['year'],
                                    d['month'],
                                    d['day'],
                                    d['fullname'],
                                    d['nationality'],
                                    d['double_nationality'],
                                    occ)
        csvstring = csvstring + line
    return csvstring

if __name__ == "__main__":
    # USE THE SCRIPT BY FOLLOWING THESE LINES
    # Uncomment the following to gather all wikipedia date pages
    # fetchallpages()
    # Uncomment the following line to parse all bdays
    # getallbdays()
    # Uncomment the following line to parse all bdays witl ml
    getallbdays_ml()

    #USED FOR DEBUGGING ######################################################
    # print(parseline_ml("711 BC - Emperor Jimmu of Japan",1,1))
    # print(parseline_ml("1466 - Elizabeth of York",1,1))
    # print(parseline_ml("1322 - John Henry, Margrave of Moravia,",1,1))

    # bdays = getbdays(3,6)
    # print(len(bdays))
    # print(is_nationality("german"))
    # i = 25
    # print(bdays[i].strip().encode('utf-8'))
    # print(parseline_ml(bdays[i], 3, 6))
    # for s in bdays:
    #    print(s.strip().encode('utf-8'))
    #    try:
    #        print(parseline_ml(s, 3, 6))
    #    except:
    #        print(s.strip().encode('utf-8'))
