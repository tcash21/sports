import time
import urllib2
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
    url = urllib2.urlopen('http://scores.espn.go.com/ncf/scoreboard')
    soup = bs(url.read(), ['fast', 'lxml'])
    #soup = bs(open('testPage1.html'))
    game_status = soup.findAll('p', id=re.compile('\d+-statusText'))
    current_week = soup.find('div', {'class':'sc_logo'}).nextSibling.text
    #rx = re.compile('(1st|2nd')
    ht = re.compile('Half')

    # ## only grab the live game IDs up until halftime
    # for game in game_status:
    #     if (re.search(rx, game.text)):
    #         ids.append(re.search("(\d+)", game["id"]).group())
    #         times.append(game.text)

    ## freeze updates at the half
    for game in game_status:
        if (re.search(ht, game.text) and re.search("(\d+)", game["id"]).group() not in halftime_ids):
            halftime_ids.append(re.search("(\d+)", game["id"]).group())

    league = 'ncf'

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
	    divs = soup.findAll('div', {'class':'mod-header'})
            for div in divs:
                if(div.h4.contents[0] == 'Team Stat Comparison'):
                    the_div = div
                    box_score = the_div.next_sibling
                    teams = box_score.find('tr', {'class':'team-color-strip'})
                    team1 = teams.findAll('th')[1].contents[1]
                    team2 = teams.findAll('th')[2].contents[1]
                    teams = [team1, team2]
                    stats = box_score.findAll('td')
                    stat_list = []

                    try:
                        with db:
                            db.execute('''INSERT INTO games(game_id, team1, team2, game_date) VALUES(?,?,?,?)''', (halftime_ids[i], team1, team2, gdate))
                            db.commit()
                            for stat in stats:
                                try:
                                    stat_list.append(stat.div.contents[0])
                                except:
                                    stat_list.append(stat.contents[0])

                            first_down_i = stat_list.index('1st Downs')
                            first_downs_a = stat_list[first_down_i + 1]
                            first_downs_b = stat_list[first_down_i + 2]
                            first_downs = [first_downs_a, first_downs_b]

                            third_down_i = stat_list.index('3rd down efficiency')
                            third_down_a = stat_list[third_down_i + 1]
                            third_down_b = stat_list[third_down_i + 2]
                            third_downs = [third_down_a, third_down_b]

                            fourth_down_i = stat_list.index('4th down efficiency')
                            fourth_down_a = stat_list[fourth_down_i + 1]
                            fourth_down_b = stat_list[fourth_down_i + 2]
                            fourth_downs = [fourth_down_a, fourth_down_b]

                            total_yards_i = stat_list.index('Total Yards')
                            total_yards_a = stat_list[total_yards_i+1]
                            total_yards_b = stat_list[total_yards_i+2]
                            total_yards = [total_yards_a, total_yards_b]        

                            passing_i = stat_list.index('Passing')
                            passing_a = stat_list[passing_i+1]
                            passing_b = stat_list[passing_i+2]
                            passing = [passing_a, passing_b]

                            comp_att_i = stat_list.index('Comp-Att')
                            comp_att_a = stat_list[comp_att_i+1]
                            comp_att_b = stat_list[comp_att_i+2]
                            comp_att = [comp_att_a, comp_att_b]

                            yards_per_pass_i = stat_list.index('Yards per pass')
                            yards_per_pass_a = stat_list[yards_per_pass_i+1]
                            yards_per_pass_b = stat_list[yards_per_pass_i+2]
                            yards_per_pass = [yards_per_pass_a, yards_per_pass_b]

                            rushing_i = stat_list.index('Rushing')
                            rushing_a = stat_list[rushing_i+1]
                            rushing_b = stat_list[rushing_i+2]
                            rushing = [rushing_a, rushing_b]

                            rushinga_i = stat_list.index('Rushing Attempts')
                            rushinga_a = stat_list[rushinga_i+1]
                            rushinga_b = stat_list[rushinga_i+2]
                            rushinga = [rushinga_a, rushinga_b]

                            yards_per_rush_i = stat_list.index('Yards per rush')
                            yards_per_rush_a = stat_list[yards_per_rush_i+1]
                            yards_per_rush_b = stat_list[yards_per_rush_i+2]
                            yards_per_rush = [yards_per_rush_a, yards_per_rush_b]

                            penalties_i = stat_list.index('Penalties')
                            penalties_a = stat_list[penalties_i+1]
                            penalties_b = stat_list[penalties_i+2]
                            penalties = [penalties_a, penalties_b]

                            turnovers_i = stat_list.index('Turnovers')
                            turnovers_a = stat_list[turnovers_i+1]
                            turnovers_b = stat_list[turnovers_i+2]
                            turnovers = [turnovers_a, turnovers_b]

                            fumbles_lost_i = stat_list.index('Fumbles lost')
                            fumbles_lost_a = stat_list[fumbles_lost_i+1]
                            fumbles_lost_b = stat_list[fumbles_lost_i+2]
                            fumbles_lost = [fumbles_lost_a, fumbles_lost_b]

                            ints_thrown_i = stat_list.index('Interceptions thrown')
                            ints_thrown_a = stat_list[ints_thrown_i+1]
                            ints_thrown_b = stat_list[ints_thrown_i+2]
                            ints_thrown = [ints_thrown_a, ints_thrown_b]

                            possession_i = stat_list.index('Possession')
                            possession_a = stat_list[possession_i+1]
                            possession_b = stat_list[possession_i+2]
                            possession = [possession_a, possession_b]
                            #print '0:' + halftime_ids[i] + ' 1:' + team1 + ' 2:' + first_downs_a + ' 3:' + third_down_a + ' 4:' + fourth_down_a + ' 5:' + total_yards_a + ' 6:' + passing_a + ' 7:' + comp_att_a + ' 8:' + rushinga + ' 9:' + yards_per_rush_a
                            try:
                                with db:
                                    db.execute('''INSERT INTO stats(game_id, team, first_downs, third_downs, fourth_downs, total_yards, passing, comp_att, 
                                                    yards_per_pass, rushing, rushing_attempts, yards_per_rush, penalties, turnovers, fumbles_lost, ints_thrown,
                                                    possession ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (halftime_ids[i], team1, int(first_downs_a), third_down_a,fourth_down_a,int(total_yards_a),int(passing_a),comp_att_a,float(yards_per_pass_a),int(rushing_a),int(rushinga_a),float(yards_per_rush_a),penalties_a,int(turnovers_a),int(fumbles_lost_a),int(ints_thrown_a),possession_a))
                                    db.commit()
                            except sqlite3.IntegrityError:
                                print('Error inserting data')

                            try:
                                with db:
                                    db.execute('''INSERT INTO stats(game_id, team, first_downs, third_downs, fourth_downs, total_yards, passing, comp_att, 
                                                    yards_per_pass, rushing, rushing_attempts, yards_per_rush, penalties, turnovers, fumbles_lost, ints_thrown,
                                                    possession ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (halftime_ids[i], team2, int(first_downs_b), third_down_b,fourth_down_b,int(total_yards_b),int(passing_b),comp_att_b,float(yards_per_pass_b),int(rushing_b),int(rushinga_b),float(yards_per_rush_b),penalties_b,int(turnovers_b),int(fumbles_lost_b),int(ints_thrown_b),possession_b))
                                    db.commit()
                            except sqlite3.IntegrityError:
                                print('Error inserting data')
                    except sqlite3.IntegrityError:
                        print('Record already exists')

                    

                    #data = [first_downs, third_downs, fourth_downs, total_yards, passing, comp_att, rushing, rushinga, yards_per_rush, penalties, turnovers, fumbles_lost, ints_thrown, possession]
                    #result = pd.DataFrame(data)
                    #result.index = ['First Downs', 'Third Downs', 'Fourth Downs', 'Total Yards', 'Passing', 'Completion Attempts', 'Rushing', 'Rushing Attempts', 'Yards Per Rush', 'Penalties', 'Turnovers', 'Fumbles Lost', 'Ints Thrown', 'Possession']    
                    #result.columns = teams
                    #results.append(result)

                else:
                    print 'Trying next div'

index()

db.close()

