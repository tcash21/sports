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
    url = urllib2.urlopen('http://scores.espn.go.com/ncb/scoreboard?date=20141216&breakdown=top25')
    soup = bs(url.read(), ['fast', 'lxml'])
    #soup = bs(open('testPage1.html'))
    game_status = soup.findAll('p', id=re.compile('\d+-statusLine'))
    links = soup.findAll('a', href=re.compile('/ncb/boxscore.*'))
    urls = [link.get('href') for link in links]
    matches=[re.search('gameId=(\d+)', u) for u in urls]
    ids = [m.group(1) for m in matches]
    #current_week = soup.find('div', {'class':'sc_logo'}).nextSibling.text
    #rx = re.compile('(1st|2nd')
    ht = re.compile('Final')

    # ## only grab the live game IDs up until halftime
    # for game in game_status:
    #     if (re.search(rx, game.text)):
    #         ids.append(re.search("(\d+)", game["id"]).group())
    #         times.append(game.text)

    ## freeze updates at the half
    for game in game_status:
        if (re.search(ht, game.text) and re.search("(\d+)", game["id"]).group() not in halftime_ids):
            halftime_ids.append(re.search("(\d+)", game["id"]).group())
    league = 'ncb'
    if(len(halftime_ids) == 0):
        print "No Halftime Box Scores yet."
    else:
        for i in range(0, len(halftime_ids)):
            espn = 'http://scores.espn.go.com/' + league + '/boxscore?gameId=' + halftime_ids[i]
            url = urllib2.urlopen(espn)
            soup = bs(url.read(), ['fast', 'lxml'])
            #soup = bs(open('testPage2.html'))
            game_date = soup.findAll('div', {'class':'game-time-location'})[0].p.text
            the_date =  re.search(',\s(.*)', game_date).group(1)
            t=time.strptime(the_date, "%B %d, %Y")
            gdate=time.strftime('%m/%d/%Y', t)
            boxscore = soup.find('table', {'class':'mod-data'})
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
            team1_data = the_thead.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling
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
                    db.execute('''INSERT INTO NCAAgames(game_id, team1, team2, game_date) VALUES(?,?,?,?)''', (halftime_ids[i], team1, team2, gdate))
                    db.commit()
            except sqlite3.IntegrityError:
                print('Error inserting data')
            try:
                db.execute('''INSERT INTO NCAAstats(game_id, team, fgma, tpma, ftma, oreb, dreb, reb, ast, stl, blk, turnovers, pf, pts ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (halftime_ids[i], team1, cleaned1[2], cleaned1[3], cleaned1[4], int(cleaned1[5]), int(cleaned1[6]), int(cleaned1[7]), int(cleaned1[8]), int(cleaned1[9]), int(cleaned1[10]), int(cleaned1[11]), int(cleaned1[12]), int(cleaned1[13])))
                db.commit()
            except sqlite3.IntegrityError:
                print('Error inserting data')
            try:
                db.execute('''INSERT INTO NCAAstats(game_id, team, fgma, tpma, ftma, oreb, dreb, reb, ast, stl, blk, turnovers, pf, pts ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (halftime_ids[i], team2, cleaned2[2], cleaned2[3], cleaned2[4], int(cleaned2[5]), int(cleaned2[6]), int(cleaned2[7]), int(cleaned2[8]), int(cleaned2[9]), int(cleaned2[10]), int(cleaned2[11]), int(cleaned2[12]), int(cleaned2[13])))
                db.commit()
            except sqlite3.IntegrityError:
                print('Error inserting data')
index()
db.close()

