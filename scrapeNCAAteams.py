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
    url = urllib2.urlopen('http://scores.espn.go.com/ncb/scoreboard')
    soup = bs(url.read(), ['fast', 'lxml'])
    links = soup.findAll('a', href=re.compile('conversation|preview.*'))
    urls = [link.get('href') for link in links]
    link_strings = [l['href'] for l in links]
    ## freeze updates at the half
    for i in range(0, len(link_strings)):
        print str(i) + ' out of ' + str(len(link_strings)) + ' teams.'
        espn = 'http://espn.go.com' + link_strings[i]
        #id = re.search('=(\d+)', link_strings[i]).group(1)
        url = urllib2.urlopen(espn)
        soup = bs(url.read(), ['fast', 'lxml'])
        teams = soup.findAll('td', {'class':'team'})
        if re.search('preview', espn):
            team1 = teams[0].strong.text
            team2 = teams[1].strong.text
        else:
            team1 = teams[1].text
            team2 = teams[2].text
        team1_id = re.search('id/(\d+)/', teams[0].a['href']).group(1)
        team2_id = re.search('id/(\d+)/', teams[1].a['href']).group(1)
        team1_url = urllib2.urlopen('http://espn.go.com/mens-college-basketball/team/stats/_/id/' + team1_id)
        soup1 = bs(team1_url.read(), ['fast', 'lxml'])
        totals = soup1.find_all('tr', {'class':'total'})[1]
        data = totals.findAll('td')
        values = [d.text for d in data]
        cols = soup1.findAll('tr', {'class':'colhead'})[1]
        colnames = cols.findAll('a')
        colnames = [c.text for c in colnames]
        try:
            with db:
                db.execute('''INSERT INTO NCAAseasonstats(team, the_date, min, fgm, fga, ftm, fta, tpm, tpa, pts, offr, defr, reb, ast, turnovers, stl, blk) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team1, time.strftime("%m/%d/%Y"),values[1],int(values[2]),int(values[3]),int(values[4]),int(values[5]),int(values[6]),int(values[7]),int(values[8]),int(values[9]),int(values[10]),int(values[11]),int(values[12]),int(values[13]),int(values[14]),int(values[15])))
                db.commit()
        except sqlite3.IntegrityError:
            print 'Record Exists'
        team2_url = urllib2.urlopen('http://espn.go.com/mens-college-basketball/team/stats/_/id/' + team2_id)
        soup2 = bs(team2_url.read(), ['fast', 'lxml'])
        totals = soup2.find_all('tr', {'class':'total'})[1]
        data = totals.findAll('td')
        values = [d.text for d in data]
        cols = soup2.findAll('tr', {'class':'colhead'})[1]
        colnames = cols.findAll('a')
        colnames = [c.text for c in colnames]
        try:
            with db:
                db.execute('''INSERT INTO NCAAseasonstats(team, the_date, min, fgm, fga, ftm, fta, tpm, tpa, pts, offr, defr, reb, ast, turnovers, stl, blk) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team2, time.strftime("%m/%d/%Y"),values[1],int(values[2]),int(values[3]),int(values[4]),int(values[5]),int(values[6]),int(values[7]),int(values[8]),int(values[9]),int(values[10]),int(values[11]),int(values[12]),int(values[13]),int(values[14]),int(values[15])))
                db.commit()
        except sqlite3.IntegrityError:
            print 'Record Exists'

index()
db.close()

