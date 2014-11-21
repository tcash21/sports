import urllib2
import re
import random
import datetime
from urlparse import urlparse
from bs4 import BeautifulSoup as bs
from flask import Flask
from flask import render_template
import pandas as pd
application = Flask(__name__)

application.debug=True

@application.route("/index/")
@application.route("/")

def index():
    results = []
    url = urllib2.urlopen('http://scores.espn.go.com/ncf/scoreboard')
    #print url.geturl()
    soup = bs(url.read(), ['fast', 'lxml'])
    #div = soup.find('div', {'class': 'span-2 0-gameCount'})
    links = soup.findAll('a', href=re.compile('/ncf/boxscore.*'))
    urls = [link.get('href') for link in links]
    matches=[re.search('gameId=(\d+)', u) for u in urls]
    ids = [m.group(1) for m in matches]
    league = 'ncf'

    ids = set(ids)
    ids = list(ids)

    if(len(ids) == 0):
        return render_template('index.html', title='No Data Yet', error='No Live Games')
    else:
        for id in ids:
            espn = 'http://scores.espn.go.com/' + league + '/boxscore?gameId=' + id 
            url = urllib2.urlopen(espn)
            soup = bs(url.read(), ['fast', 'lxml'])
            divs = soup.findAll('div', {'class':'mod-header'})
            for div in divs:
                try:
                    if(div.h4.contents[0] == 'Team Stat Comparison'):
                        the_div = div
                except:
                    print 'unexpected error'

            box_score = the_div.next_sibling
            teams = box_score.find('tr', {'class':'team-color-strip'})
            team1 = teams.findAll('th')[1].contents[1]
            team2 = teams.findAll('th')[2].contents[1]
            teams = [team1, team2]
            stats = box_score.findAll('td')
            stat_list = []

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
        
            data = [first_downs, third_downs, fourth_downs, total_yards, passing, comp_att, rushing, rushinga, yards_per_rush, penalties, turnovers, fumbles_lost, ints_thrown, possession]
            result = pd.DataFrame(data)
            result.index = ['First Downs', 'Third Downs', 'Fourth Downs', 'Total Yards', 'Passing', 'Completion Attempts', 'Rushing', 'Rushing Attempts', 'Yards Per Rush', 'Penalties', 'Turnovers', 'Fumbles Lost', 'Ints Thrown', 'Possession']    
            result.columns = teams

        results.append(result)
                # print 'Category,' + team1 + ',' + team2
                # print '1st Downs, ' + first_downs_a + ',' + first_downs_b
                # print '3rd down efficiency,="' + third_down_a + '",="' + third_down_b + '"'
                # print '4th down efficiency,="' + fourth_down_a + '",="' + fourth_down_b + '"'
                # print 'Total Yards, ' + total_yards_a + ',' + total_yards_b
                # print 'Passing, ' + passing_a + ',' + passing_b
                # print 'Comp-Att,="' + comp_att_a + '",="' + comp_att_b + '"'
                # print 'Rushing, ' + rushing_a + ',' + rushing_b
                # print 'Rushing Attempts, ' + rushinga_a + ',' + rushinga_b
                # print 'Yards per rush,' + yards_per_rush_a + ',' + yards_per_rush_b
                # print 'Penalties,="' + penalties_a + '",="' + penalties_b + '"'
                # print 'Turnovers, ' + turnovers_a + ',' + turnovers_b
                # print 'Fumbles lost, ' + fumbles_lost_a + ',' + fumbles_lost_b
                # print 'Interceptions thrown, ' + ints_thrown_a + ',' + ints_thrown_b
                # print 'Possession,="' + possession_a + '",="' + possession_b + '"'
                # print ''
    return render_template('index.html', title='Live Game Box Scores', results=results)

if __name__ == '__main__':
    application.run()
