import requests, re
r = requests.get('https://en.wikipedia.org/wiki/March_6')



#births_section_pattern = re.compile('DOC', re.MULTILINE)

#births_section = re.search('(Births)','>Births</span><span class') #r.content
births_pattern = '<span class="mw-headline" id="Births">.*<span class="mw-headline" id="Deaths">'
births_section = re.search(births_pattern, r.content.replace('\n','\00'))

births_section = births_section.group()
#births_section = births_section.replace('<li>', '\00')
births_section = births_section.replace('</li>', '\n')

items_pattern = r'<li>.*'
births_items = re.findall(items_pattern, births_section)

#print isinstance(births_section.group(), basestring)
print len(births_items)
print births_items[-1]
