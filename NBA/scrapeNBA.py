__author__ = 'tanyacashorali'

import jsonpickle
import random
import urllib2
import time
import re
import random
from datetime import date
import datetime
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
    #soup = bs(open('testPage1.html'))
    scoreboard=soup.findAll('div', {'id': 'scoreboard-page'})
    data=scoreboard[0].get('data-data')
    j=jsonpickle.decode(data)
    games=j['events']
    status = [game['status'] for game in games]
    half = [s['type']['shortDetail'] for s in status]
    index = [i for i, j in enumerate(half) if j == 'Halftime']
    ids = [game['id'] for game in games]
    halftime_ids = [j for k, j in enumerate(ids) if k in index]

    league = 'nba'
    if(len(halftime_ids) == 0):
        print "No Halftime Box Scores yet."
    else:
        for i in range(0, len(halftime_ids)):
            x=random.randint(5, 10)
            time.sleep(x)
            espn = 'http://scores.espn.go.com/' + league + '/boxscore?gameId=' + halftime_ids[i]
            url = urllib2.urlopen(espn)
            soup = bs(url.read(), ['fast', 'lxml'])
            #soup = bs(open('testPage2.html'))
            game_date = soup.findAll('div', {'class':'game-time-location'})[0].p.text
            the_date =  re.search(',\s(.*)', game_date).group(1)
            the_time = re.search('^(.*?),', game_date)
            game_time = the_time.group(1)
            t=time.strptime(the_date, "%B %d, %Y")
            gdate=time.strftime('%m/%d/%Y', t)
            boxscore = soup.find('table', {'class':'mod-data'})
            strong = soup.find_all('strong', text=re.compile('Officials')          
            officials = strong[0].next_sibling
            try: 
                theads=boxscore.findAll('thead')
                the_thead = None
                for thead in theads:
                    ths=thead.findAll('th')
                    labels = [x.text for x in ths]
                    if (any("TOTALS" in s for s in labels)):
                        the_thead = thead
                        break
                headers = the_thead.findAll('th')
                header_vals = [h.text for h in headers]
                team1_data = the_thead.nextSibling
                tds = team1_data.findAll('td')
                values = [v.text for v in tds]
                remove = [v == '' for v in values]
                remove_indices = [a for a, b in enumerate(remove) if b]
                cleaned1 = [j for k, j in enumerate(values) if k not in remove_indices]
                linescore = soup.find('table', {'class':'linescore'})
                team1 = linescore.findAll('a')[0].text
                team2 = linescore.findAll('a')[1].text
                team1_data = the_thead.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling
                tds = team1_data.findAll('td')
                values = [v.text for v in tds]
                remove = [v == '' for v in values]
                remove_indices = [j for j, x in enumerate(remove) if x]
                cleaned2 = [j for k, j in enumerate(values) if k not in remove_indices]
                cleaned1.insert(0, team1)
                cleaned2.insert(0, team2)
                cleaned1.insert(0, halftime_ids[i])
                cleaned2.insert(0, halftime_ids[i])
                cleaned1.pop()
                cleaned1.pop()
                cleaned1.pop()
                cleaned2.pop()
                cleaned2.pop()
                cleaned2.pop()
                try:
                    with db:
                        db.execute('''INSERT INTO NBAgames(game_id, team1, team2, game_date, game_time, officials) VALUES(?,?,?,?,?,?)''', (halftime_ids[i], team1, team2, gdate, game_time, officials))
                        db.commit()
                    try:
                        date_time = str(datetime.datetime.now())
                        db.execute('''INSERT INTO NBAstats(game_id, team, fgma, tpma, ftma, oreb, dreb, reb, ast, stl, blk, turnovers, pf, pts, timestamp ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (halftime_ids[i], team1, cleaned1[2], cleaned1[3], cleaned1[4], int(cleaned1[5]), int(cleaned1[6]), int(cleaned1[7]), int(cleaned1[8]), int(cleaned1[9]), int(cleaned1[10]), int(cleaned1[11]), int(cleaned1[12]), int(cleaned1[14]), date_time))
                        db.commit()
                    except sqlite3.IntegrityError:
                        print sqlite3.Error
                    try:
                        date_time = str(datetime.datetime.now())
                        db.execute('''INSERT INTO NBAstats(game_id, team, fgma, tpma, ftma, oreb, dreb, reb, ast, stl, blk, turnovers, pf, pts, timestamp ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (halftime_ids[i], team2, cleaned2[2], cleaned2[3], cleaned2[4], int(cleaned2[5]), int(cleaned2[6]), int(cleaned2[7]), int(cleaned2[8]), int(cleaned2[9]), int(cleaned2[10]), int(cleaned2[11]), int(cleaned2[12]), int(cleaned2[14]), date_time))
                        db.commit()
                    except sqlite3.IntegrityError:
                        print sqlite3.Error            
                except sqlite3.IntegrityError:
                    print 'Record Already Exists'    
            except:
                print 'No Boxscore Available'     
index()
db.close()

