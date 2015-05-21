__author__ = 'tanyacashorali'

import random
import urllib2
import time
import re
import random
from datetime import date
import os
import sqlite3
import pandas as pd
from urlparse import urlparse
from bs4 import BeautifulSoup as bs

db = sqlite3.connect('/home/ec2-user/sports/sports.db')


x=random.randint(1, 20)
time.sleep(x)

def index():
    print "entered index"
    times = []
    halftime_ids = []
    today = date.today()
    today = today.strftime("%Y%m%d")
    url = urllib2.urlopen('http://scores.espn.go.com/nba/scoreboard?date=' + today)
    soup = bs(url.read(), ['fast', 'lxml'])
    #scoreboard=soup.findAll('div', {'id': 'scoreboard-page'})
    #data=scoreboard[0].get('data-data')
    teams = re.findall('http://espn.go.com/nba/team/_/name/(\w+)', str(soup))

    for i in range(0, len(teams)):
        x=random.randint(5, 10)
        time.sleep(x)
        print str(i) + ' out of ' + str(len(teams)) + ' teams.'
        espn = 'http://espn.go.com/nba/team/stats/_/name/' + teams[i]
        print espn
        #id = re.search('=(\d+)', link_strings[i]).group(1)
        url = urllib2.urlopen(espn)
        soup1 = bs(url.read(), ['fast', 'lxml'])
        
        ## e.g. no season stats for http://espn.go.com/mens-college-basketball/team/stats/_/id/2395
        try:
            totals1 = soup1.find_all('tr', {'class':'total'})[1]
            data1 = totals1.findAll('td')
            values1 = [d.text for d in data1]
            cols1 = soup1.findAll('tr', {'class':'colhead'})[1]
            colnames1 = cols1.findAll('a')
            colnames1 = [c.text for c in colnames1]

            totals0 = soup1.find_all('tr', {'class':'total'})[0]
            data0 = totals0.findAll('td')
            values0 = [d.text for d in data0]
            cols0 = soup1.findAll('tr', {'class':'colhead'})[0]
            colnames0 = cols0.findAll('a')
            colnames0 = [c.text for c in colnames0]

            try:
                with db:
                    db.execute('''INSERT INTO NBAseasonstats(team, the_date, fgm, fga, fgp, tpm, tpa, tpp, ftm, fta, ftp, twopm, twopa, twopp, pps, afg) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (teams[i].upper(), time.strftime("%m/%d/%Y"),float(values1[1]),float(values1[2]),float(values1[3]),float(values1[4]),float(values1[5]),float(values1[6]),float(values1[7]),float(values1[8]),float(values1[9]),float(values1[10]),float(values1[11]),float(values1[12]),float(values1[13]),float(values1[14])))
                    db.commit()
            except sqlite3.IntegrityError:
                print 'Team1 Season Stats Already Exist!'
            try: 
                with db:
                    db.execute('''INSERT INTO NBAseasontotals(team, the_date, gp, ppg, orpg, defr, rpg, apg, spg, bpg, tpg, fpg, ato) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (teams[i].upper(), time.strftime("%m/%d/%Y"), int(values0[1]),  float(values0[4]), float(values0[5]), float(values0[6]), float(values0[7]), float(values0[8]), float(values0[9]), float(values0[10]), float(values0[11]), float(values0[12]), float(values0[13])))
                    db.commit()
            except sqlite3.IntegrityError:
                print 'Team1 Season Totals Already Exist!'
        except:
            print 'No stats for team1'

index()
db.close()

