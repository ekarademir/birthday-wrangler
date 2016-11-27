# birthday-wrangler.py
A data wrangler using Python to crawl, sift, and store birthday dates of well known people from date pages on Wikipedia.

This was a project that I've done previously with PHP. Here, I develop the same project with Python. This is an exercise for me to learn about http interfacing with **requests** and text parsing.

* Built on Python 2.7
* **Updated to run on Python 3.5**

# Update 1
* Implemented deep learning to guess the nationality

# Issues
* For now, there is a very crude extraction method for names, nationalities
  and occupations. Each line should be in a certain format or it will be ignored.
  Can't extract Albert Einstein yet :/
* There is no wrapper. So use the main function to run the commands.
* Assumes everything is found and existing.

# Usage
In the main function,

- Uncomment _fetchallpages()_ to fetch all Wikipedia pages to disk
- Uncomment _getallbdays()_ to parse saved files. Resulting CSV file contains
  one entry per occupation, hence, birthdays are matched with occupations.
