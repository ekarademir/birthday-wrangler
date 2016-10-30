def fetchbdays(wikipage='https://en.wikipedia.org/wiki/March_6'):
    import requests, re

    # Fetch the contents of the date page
    r = requests.get(wikipage)

    # Seperate the birth section [everything between span classes of Births and Deaths]
    # Before the regex search flatten the content string into one line
    births_pattern = '<span class="mw-headline" id="Births">.*<span class="mw-headline" id="Deaths">'
    births_section = re.search(births_pattern, r.content.replace('\n','\00'))

    # After seperating out the births section we can unflatten it again using end tags if li
    births_section = births_section.group()
    births_section = births_section.replace('</li>', '\n')

    # Get all li elements. Later we will clean up these tags.
    items_pattern = r'<li>.*'
    births_items = re.findall(items_pattern, births_section)

    # Clean up the HTML tags
    replace_pattern = r'<.*?>'
    births_items = map(lambda x: re.sub(replace_pattern, '\00',x), births_items)

    return births_items

if __name__ == "__main__":
    bdays = fetchbdays()
    print len(bdays)
