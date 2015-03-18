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
    vals = [50,55,56,100]
    for v in range(0,3):
        url = urllib2.urlopen('http://scores.espn.go.com/ncb/scoreboard?date=' + today + '&confId=' + str(vals[v]))
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
            x=random.randint(5, 15)
            time.sleep(x)
            print str(i) + ' out of ' + str(len(link_strings)) + ' teams.'
            espn = 'http://espn.go.com' + link_strings[i]
            print espn
            #id = re.search('=(\d+)', link_strings[i]).group(1)
            url = urllib2.urlopen(espn)
            soup = bs(url.read(), ['fast', 'lxml'])
            teams = soup.findAll('td', {'class':'team'})
            team1 = teams[0].strong.text
            team2 = teams[1].strong.text
            if team1 == 'WM':
                team1 = 'W&M'
            if team2 == 'WM':
                team2 = 'W&M'
            if team1 == 'TAM':
                team1 = 'TA&M'
            if team2 == 'TAM':
                team2 = 'TA&M'
            team1_id = re.search('id/(\d+)/', teams[0].a['href']).group(1)
            team2_id = re.search('id/(\d+)/', teams[1].a['href']).group(1)
            team1_url = urllib2.urlopen('http://espn.go.com/mens-college-basketball/team/stats/_/id/' + team1_id)
            soup1 = bs(team1_url.read(), ['fast', 'lxml'])
            ## e.g. no season stats for http://espn.go.com/mens-college-basketball/team/stats/_/id/2395
            try:
                totals0 = soup1.find_all('tr', {'class':'total'})[0]
                data0 = totals0.findAll('td')
                values0 = [d.text for d in data0]
                cols0 = soup1.findAll('tr', {'class':'colhead'})[0]
                colnames0 = cols0.findAll('a')
                colnames0 = [c.text for c in colnames0]

                totals1 = soup1.find_all('tr', {'class':'total'})[1]
                data = totals1.findAll('td')
                values = [d.text for d in data]
                cols = soup1.findAll('tr', {'class':'colhead'})[1]
                colnames = cols.findAll('a')
                colnames = [c.text for c in colnames]
                try:
                    with db:
                        db.execute('''INSERT INTO NCAAseasonstats(team, the_date, min, fgm, fga, ftm, fta, tpm, tpa, pts, offr, defr, reb, ast, turnovers, stl, blk) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team1, time.strftime("%m/%d/%Y"),values[1],int(values[2]),int(values[3]),int(values[4]),int(values[5]),int(values[6]),int(values[7]),int(values[8]),int(values[9]),int(values[10]),int(values[11]),int(values[12]),int(values[13]),int(values[14]),int(values[15])))
                        db.commit()
                except sqlite3.IntegrityError:
                    print 'Team1 Season Stats Record Exists'
                try:
                    with db:
                        db.execute('''INSERT INTO NCAAseasontotals(team, the_date, gp, min, ppg, rpg, apg, spg, bpg, tpg, fgp, ftp, tpp) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team1, time.strftime("%m/%d/%Y"), int(values0[1]), values0[2], int(values0[3]), int(values0[4]), int(values0[5]), int(values0[6]), int(values0[7]), int(values0[8]), float(values0[9]), float(values0[10]), float(values0[11])))
                        db.commit()
                except sqlite3.IntegrityError:
                    print 'Team1 Season Totals Record Exists'   
            except:
                print 'No stats for team'

            team2_url = urllib2.urlopen('http://espn.go.com/mens-college-basketball/team/stats/_/id/' + team2_id)
            soup2 = bs(team2_url.read(), ['fast', 'lxml'])
            try:
                totals0 = soup2.find_all('tr', {'class':'total'})[0]
                data0 = totals0.findAll('td')
                values0 = [d.text for d in data0]
                cols0 = soup1.findAll('tr', {'class':'colhead'})[0]
                colnames0 = cols0.findAll('a')
                colnames0 = [c.text for c in colnames0]

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
                    print 'Team2 Season Stats Record Exists'
                try:
                    with db:
                        db.execute('''INSERT INTO NCAAseasontotals(team, the_date, gp, min, ppg, rpg, apg, spg, bpg, tpg, fgp, ftp, tpp) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (team2, time.strftime("%m/%d/%Y"), int(values0[1]), values0[2], int(values0[3]), int(values0[4]), int(values0[5]), int(values0[6]), int(values0[7]), int(values0[8]), float(values0[9]),float(values0[10]),float(values0[11])))
                        db.commit()
                except sqlite3.IntegrityError:
                    print 'Team2 Season Totals Record Exists'
              
            except:
                print 'No stats for team'

index()
db.close()


