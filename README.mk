# Hashtag Parser

This program is designed to periodically query Twitter for mentions of a
hashtag and produce a frequency graph of the usernames mentioned in the
tweets. Due to a lack of a developer key (Curse you yet again Twitter),
this uses a simple HTTP GET request and parses the resultant HTML. This
makes it somewhat slow, but servicable for all but the hottest tags. The
output is stored in a .csv format.

## Requirements
- Python2.7
- BeautifulSoup

To install Python:
```
sudo apt-get install python2.7
```
To install BeautifulSoup:
```
pip install BeautifulSoup
```
