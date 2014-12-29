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

db = sqlite3.connect('/home/ec2-user/sports/sports.db')

def index():
    print "entered index"
    times = []
    halftime_ids = []
    url = urllib2.urlopen('http://espn.go.com/mens-college-basketball/teams')
    soup = bs(url.read(), ['fast', 'lxml'])
    links = soup.findAll('a', href=re.compile('stats.*'))
    urls = [link.get('href') for link in links]
    link_strings = [l['href'] for l in links]
    ## freeze updates at the half
    for i in range(0, len(link_strings)):
        espn = 'http://espn.go.com' + link_strings[i]
        id = re.search('=(\d+)', link_strings[i]).group(1)
        url = urllib2.urlopen(espn)
        soup = bs(url.read(), ['fast', 'lxml'])
        totals = soup.find_all('tr', {'class':'total'})[1]
        data = totals.findAll('td')
        values = [d.text for d in data]
        cols = soup.findAll('tr', {'class':'colhead'})[1]
        colnames = cols.findAll('a')
        colnames = [c.text for c in colnames]
        clubhouse = urllib2.urlopen('http://espn.go.com/mens-college-basketball/team/_/id/' + str(id))
        clubsoup = bs(clubhouse.read(), ['fast', 'lxml'])
        recap = clubsoup.findAll('a', href=re.compile('recap'))[0]['href']
        a_url = urllib2.urlopen('http://espn.go.com' + recap)
        recapsoup = bs(a_url.read(), ['fast', 'lxml'])
        team = recapsoup.findAll('td', {'class':'team'})
        id1 = int(re.search('id/(\d+)/', str(team[1])).group(1))
        id2 = int(re.search('id/(\d+)/', str(team[2])).group(1))
        abbr = ''
        if id == id1:
            abbr = team[1].text
        else:
            abbr = team[2].text
        try:
            with db:
                db.execute('''INSERT INTO NCAAseasonstats(team, the_date, min, fgm, fga, ftm, fta, tpm, tpa, pts, offr, defr, reb, ast, turnovers, stl, blk) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (abbr, time.strftime("%m/%d/%Y"),values[1],int(values[2]),int(values[3]),int(values[4]),int(values[5]),int(values[6]),int(values[7]),int(values[8]),int(values[9]),int(values[10]),int(values[11]),int(values[12]),int(values[13]),int(values[14]),int(values[15])))
                db.commit()
        except sqlite3.IntegrityError:
            print 'Error inserting data'

index()
db.close()

