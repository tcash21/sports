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
from datetime import date, timedelta

db = sqlite3.connect('/home/ec2-user/sports/sports.db')

x=random.randint(1, 20)
time.sleep(x)

url = urllib2.urlopen('https://www.sportsbook.ag/sbk/sportsbook4/nba-betting/nba-game-lines.sbk')
soup = bs(url.read(), ['fast', 'lxml'])
the_date = date.today()

divs=soup.findAll('div', id=re.compile( the_date.strftime("%m%d%y")))
awayTeams=[d.findAll('span', {'id':'awayTeamName'}) for d in divs]
homeTeams=[d.findAll('span', {'id':'homeTeamName'}) for d in divs]
awayTeams = filter(len, awayTeams)
homeTeams = filter(len, homeTeams)
#awayTeams.pop(0)
#homeTeams.pop(0)
awayTeams=[a[0].text for a in awayTeams]
homeTeams=[h[0].text for h in homeTeams]

market=[d.findAll('div', {'class':'market'}) for d in divs]
#market.pop(0)
market=filter(len,market)
the_lines=[m[0].text for m in market]
the_spreads=[m[1].text for m in market]

lines = []
spreads = []

if len(the_lines) > len(the_spreads):
    upper = len(the_lines)
else:
    upper = len(the_spreads)

for i in range(0, upper):
    try:
        lines.append(re.search('(\d+\\.?\d+)\\(', the_lines[i]).group(1))
    except:
        lines.append(0)
        next

for i in range(0, upper):
    try:
        spreads.append(re.search('([+-]\d+\\.?\d?)\\(', the_spreads[i]).group(1))
    except:
        spreads.append(0)
        next

#today = date.today()
#today = today.strftime("%m/%d/%Y")
today = str(datetime.datetime.now() - timedelta(hours=2))[0:10]
today = time.strftime("%m/%d/%Y", time.strptime(today, '%Y-%m-%d'))

date_time = str(datetime.datetime.now())

for i in range(0, len(lines)):
    try:
        with db:
            db.execute('''INSERT INTO NBASBLines(away_team, home_team, line, spread, game_date, game_time) VALUES(?,?,?,?,?,?)''', (awayTeams[i], homeTeams[i], lines[i], spreads[i], today, date_time))
            db.commit()
    except sqlite3.IntegrityError:
        print 'Record Exists'

for i in range(0, len(lines)):
    try:
        with db:
            db.execute('''INSERT INTO NBASBteamlookup(sb_team, espn_abbr) VALUES (?,?)''', (awayTeams[i], None))
            db.execute('''INSERT INTO NBASBteamlookup(sb_team, espn_abbr) VALUES (?,?)''', (homeTeams[i], None))
    except:
        print 'Record Exists'

db.close()
