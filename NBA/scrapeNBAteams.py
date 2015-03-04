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
    links = soup.findAll('a', href=re.compile('conversation.*'))
    urls = [link.get('href') for link in links]
    link_strings = [l['href'] for l in links]
    game_status = soup.findAll('div', {'class':'game-status'})
    g_status = [g.text for g in game_status]
    remove = [v == 'Final' for v in g_status]
    remove_indices = [j for j, x in enumerate(remove) if x]
    link_strings = [j for k, j in enumerate(link_strings) if k not in remove_indices]
    ## freeze updates at the half
    for i in range(0, len(link_strings)):
        print str(i) + ' out of ' + str(len(link_strings)) + ' teams.'
        espn = 'http://espn.go.com' + link_strings[i]
        print espn
        #id = re.search('=(\d+)', link_strings[i]).group(1)
        url = urllib2.urlopen(espn)
        soup = bs(url.read(), ['fast', 'lxml'])
        teams = soup.findAll('td', {'class':'team'})
        team1 = teams[0].text
        team2 = teams[1].text
        t1 = teams[0].a["href"]
        t2 = teams[1].a["href"]
        p1 = re.search('name\/(\w+)\/(\w+)', t1).group(1)
        p2 = re.search('name\/(\w+)\/(\w+)', t1).group(2)
        p3 = re.search('name\/(\w+)\/(\w+)', t2).group(1)
        p4 = re.search('name\/(\w+)\/(\w+)', t2).group(2)
        team1_url = urllib2.urlopen('http://espn.go.com/nba/team/stats/_/name/' + p1 + '/' + p2)
        team2_url = urllib2.urlopen('http://espn.go.com/nba/team/stats/_/name/' + p3 + '/' + p4)
        soup1 = bs(team1_url.read(), ['fast', 'lxml'])
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
            colnames0 = cols1.findAll('a')
            colnames0 = [c.text for c in colnames0]

            try:
                with db:
                    db.execute('''INSERT INTO NBAseasonstats(team, the_date, min, fgm, fga, ftm, fta, tpm, tpa, pts, offr, defr, reb, ast, turnovers, stl, blk) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team1, time.strftime("%m/%d/%Y"),values1[1],int(values1[2]),int(values1[3]),int(values1[4]),int(values1[5]),int(values1[6]),int(values1[7]),int(values1[8]),int(values1[9]),int(values1[10]),int(values1[11]),int(values1[12]),float(values1[13]),float(values1[14]),float(values1[15])))
                    db.commit()
            except sqlite3.IntegrityError:
                print 'Team1 Season Stats Already Exist!'
            try: 
                with db:
                    db.execute('''INSERT INTO NBAseasontotals(team, the_date, gp, ppg, orpg, defr, rpg, apg, spg, bpg, tpg, fpg, ato) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team1, time.strftime("%m/%d/%Y"), int(values0[0]), float(values0[1]), float(values0[2]), float(values0[3]), float(values0[4]), float(values0[5]), float(values0[6]), float(values0[7]), float(values0[8]), float(values0[9]), float(values0[10])))
                    db.commit()
            except sqlite3.IntegrityError:
                print 'Team1 Season Totals Already Exist!'
        except:
            print 'No stats for team1'

        soup2 = bs(team2_url.read(), ['fast', 'lxml'])
        try:
            totals1 = soup2.find_all('tr', {'class':'total'})[1]
            data1 = totals1.findAll('td')
            values1 = [d.text for d in data1]
            cols1 = soup2.findAll('tr', {'class':'colhead'})[1]
            colnames1 = cols1.findAll('a')
            colnames1 = [c.text for c in colnames1]
       
            totals0 = soup2.find_all('tr', {'class':'total'})[0]
            data0 = totals0.findAll('td')
            values0 = [d.text for d in data0]
            cols0 = soup2.findAll('tr', {'class':'colhead'})[0]
            colnames0 = cols1.findAll('a')
            colnames0 = [c.text for c in colnames0]

            try:
                with db:
                    db.execute('''INSERT INTO NBAseasonstats(team, the_date, min, fgm, fga, ftm, fta, tpm, tpa, pts, offr, defr, reb, ast, turnovers, stl, blk) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team2, time.strftime("%m/%d/%Y"),values1[1],int(values1[2]),int(values1[3]),int(values1[4]),int(values1[5]),int(values1[6]),int(values1[7]),int(values1[8]),int(values1[9]),int(values1[10]),int(values1[11]),int(values1[12]),float(values1[13]),float(values1[14]),float(values1[15])))
                    db.commit()
            except sqlite3.IntegrityError:
                print 'Team2 Season Stats Already Exist!'
            try:
                with db:
                    db.execute('''INSERT INTO NBAseasontotals(team, the_date, gp, ppg, orpg, defr, rpg, apg, spg, bpg, tpg, fpg, ato) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team2, time.strftime("%m/%d/%Y"), int(values0[0]), float(values0[1]), float(values0[2]), float(values0[3]), float(values0[4]), float(values0[5]), float(values0[6]), float(values0[7]), float(values0[8]), float(values0[9]), float(values0[10])))
                    db.commit()
            except sqlite3.IntegrityError:
                print 'Team2 Season Totals Already Exist!'
        except:
            print 'No stats for team2'

index()
db.close()

