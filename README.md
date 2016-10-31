# birthday-wrangler.py
A data wrangler using python to crawl, sift, and store birthday dates of well known people from date pages on Wikipedia.

This was a project that I've done previously with PHP. Here, I develop the same project with Python. This is an exercise for me to learn about http interfacing with **requests** and text parsing.

Built on Python 2.7

# Issues
* For now, there is a very crude extraction method for names, nationalities
  and occupations. Each line should be in a certain format or it will be ignored.
  Can't extract Albert Einstein :/
* There is no wrapper. So use the main function to run the commands.
* Assumes everything is found and existing.

# Usage
In the main function,

- uncomment _fetchallpages()_
