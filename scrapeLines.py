__author__ = 'tanyacashorali'

import urllib2
import time
import re
import random
import datetime
import os
import sqlite3
import pandas as pd
from urlparse import urlparse
from bs4 import BeautifulSoup as bs

url = urllib2.urlopen('http://www.covers.com/odds/basketball/college-basketball-odds.aspx')
soup = bs(url.read(), ['fast', 'lxml'])
tables = soup.findAll('table')
lines = tables[2]
away = lines.findAll('div', {'class':'team_away'})
home = lines.findAll('div', {'class':'team_home'})
covers = lines.findAll('td', {'class':'covers_top'})

for i in range(0, len(covers)):
    line = covers[i].find('div', {'class':'line_top'}).text
    line_number = float(re.search('\d+\.*\d*', line).group(0))
    print line_number
    spread = covers[i].find('div', {'class':'covers_bottom'}).text
    spread_number = float(re.search('[-|+]\d+\.*\d*', spread).group(0))
    print spread_number

a_teams = filter(None, [a.strong for a in away])
h_teams = filter(None, [h.strong for h in home])

away_teams = [a.text for a in a_teams]
home_teams = [h.text for h in h_teams]
