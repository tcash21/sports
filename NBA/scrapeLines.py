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
from datetime import date

db = sqlite3.connect('/home/ec2-user/sports/sports.db')

url = urllib2.urlopen('http://www.covers.com/odds/basketball/nba-spreads.aspx')
soup = bs(url.read(), ['fast', 'lxml'])
tables = soup.findAll('table')
lines = tables[2]
away = lines.findAll('div', {'class':'team_away'})
home = lines.findAll('div', {'class':'team_home'})
covers = lines.findAll('td', {'class':'covers_top'})
today = date.today()
today = today.strftime("%m/%d/%Y")

lines = []
spreads = []

for i in range(0, len(covers)):
    line = covers[i].find('div', {'class':'line_top'}).text
    line_number = re.search('\d+\.*\d*|\w+', line).group(0)
    lines.append(line_number)
    spread = covers[i].find('div', {'class':'covers_bottom'}).text
    spread_number = re.search('[-|+]\d+\.*\d*|\w+', spread).group(0)
    spreads.append(spread_number)
 
a_teams = filter(None, [a.strong for a in away])
h_teams = filter(None, [h.strong for h in home])

away_teams = [a.text for a in a_teams]
home_teams = [h.text for h in h_teams]
## remove @ symbol for home teams
home_teams = [re.sub('@', '', h) for h in home_teams]

date_time = str(datetime.datetime.now())

for i in range(0, len(away_teams)):
    try:
        with db:
            db.execute('''INSERT INTO NBALines(away_team, home_team, line, spread, game_date, game_time) VALUES(?,?,?,?,?,?)''', (away_teams[i], home_teams[i], lines[i], spreads[i], today, date_time))
            db.commit()
    except sqlite3.IntegrityError:
        print 'Record Exists'

for i in range(0, len(away_teams)):
    try:
        with db:
            db.execute('''INSERT INTO NBAteamlookup(covers_team, espn_abbr, espn_name) VALUES (?,?,?)''', (away_teams[i], None, None))
            db.execute('''INSERT INTO NBAteamlookup(covers_team, espn_abbr, espn_name) VALUES (?,?,?)''', (home_teams[i], None, None))
    except:
        print 'Record Exists'

db.close()
