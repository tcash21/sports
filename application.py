import os
import time
import sqlite3
import pandas as pd
from flask import render_template, request, session
from flask import g
from flask import Flask

application = Flask(__name__)
application.debug = True

application.config.update(dict(
    DATABASE='/home/ec2-user/sports/sports.db',
    #DATABASE='/Users/tanyacashorali/sports/sports.db',
    DEBUG=True,
    SECRET_KEY = open("/dev/random","rb").read(32)
    #USERNAME='admin',
    #PASSWORD='default'
))
application.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(application.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@application.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@application.route('/date_select', methods=['POST', 'GET'])
def date_select():
    session['game_date'] = request.form['game_date']
    with application.app_context():
        db = get_db()
        cur = db.execute("select g.game_id, game_date FROM games g, stats s where g.game_id = s.game_id and game_date =?", (session['game_date'],))
        cur2 = db.execute("select * FROM stats s, games g where s.game_id = g.game_id and game_date = ?", (session['game_date'],))
        game_ids = cur.fetchall()
        game_ids = list(set(game_ids))
        stats = cur2.fetchall()
        if(len(stats) > 0):
            result = pd.DataFrame(stats)
            result.index = result[0]
            resultsNCF = []
            timesNCF = []
            for i in range (0, len(game_ids)):
                result2 = result.ix[game_ids[i][0]]
                teams = result2[1]
                result2 = result2.transpose()
                result2.columns = teams
                result2 = result2.ix[2:16]
                result2.index = ['First Downs', 'Third Downs', 'Fourth Downs', 'Total Yards', 'Passing', 'Completion Attempts', 'Rushing', 'Rushing Attempts', 'Yards Per Pass', 'Yards Per Rush', 'Penalties', 'Turnovers', 'Fumbles Lost', 'Ints Thrown', 'Possession']
                resultsNCF.append(result2)
                timesNCF.append(game_ids[i][1])
        curNCAA = db.execute("select g.game_id, game_date FROM NCAAgames g, NCAAstats s where g.game_id = s.game_id and game_date =?", (session['game_date'],))
        cur2NCAA = db.execute("select * FROM NCAAstats s, NCAAgames g where s.game_id = g.game_id and game_date = ?", (session['game_date'],))
        game_ids = curNCAA.fetchall()
        game_ids = list(set(game_ids))
        stats2 = cur2NCAA.fetchall()
        db.close()
        if(len(stats2) > 0):
            result = pd.DataFrame(stats2)
            result.index = result[0]
            resultsNCAA = []
            timesNCAA = []
            for i in range (0, len(game_ids)):
                result2 = result.ix[game_ids[i][0]]
                teams = result2[1]
                result2 = result2.transpose()
                result2.columns = teams
                result2 = result2.ix[2:13]
                result2.index = ['FGM-A', 'TPM-A', 'FTM-A', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'PTS']
                resultsNCAA.append(result2)
                timesNCAA.append(game_ids[i][1])
    if len(stats) > 0 and len(stats2) > 0:
        return render_template('index.html', resultsNCF=resultsNCF, timesNCF=timesNCF, resultsNCAA=resultsNCAA, timesNCAA=timesNCAA)
    elif len(stats) == 0 and len(stats2) > 0:
        return render_template('index.html', resultsNCAA=resultsNCAA, timesNCAA=timesNCAA)
    elif len(stats) > 0 and len(stats2) == 0:
        return render_template('index.html', resultsNCF=resultsNCF, timesNCF=timesNCF)
    else:
        return render_template('index.html', error='No Box Scores') 

@application.route('/')
def show_entries():
    with application.app_context():
        db = get_db()
        cur = db.execute("select g.game_id, game_date FROM games g, stats s where g.game_id = s.game_id and game_date=?", (time.strftime("%m/%d/%Y"),))
        cur2 = db.execute("select * FROM stats s, games g where s.game_id = g.game_id and game_date = ?", (time.strftime("%m/%d/%Y"),))
        game_ids = cur.fetchall()
        game_ids = list(set(game_ids))
        stats = cur2.fetchall()
        if(len(stats) > 0):
   	    result = pd.DataFrame(stats)
            result.index = result[0]
            resultsNCF = []
            timesNCF = []
            for i in range (0, len(game_ids)):
                result2 = result.ix[game_ids[i][0]]
                teams = result2[1]
                result2 = result2.transpose()
                result2.columns = teams
                result2 = result2.ix[2:16]
                result2.index = ['First Downs', 'Third Downs', 'Fourth Downs', 'Total Yards', 'Passing', 'Completion Attempts', 'Rushing', 'Rushing Attempts', 'Yards Per Pass', 'Yards Per Rush', 'Penalties', 'Turnovers', 'Fumbles Lost', 'Ints Thrown', 'Possession']    
                resultsNCF.append(result2)
                timesNCF.append(game_ids[i][1])
        curNCAA = db.execute("select g.game_id, game_date FROM NCAAgames g, NCAAstats s where g.game_id = s.game_id and game_date =?", (time.strftime("%m/%d/%Y"),))
        cur2NCAA = db.execute("select * FROM NCAAstats s, NCAAgames g where s.game_id = g.game_id and game_date = ?", (time.strftime("%m/%d/%Y"),))
        game_ids = curNCAA.fetchall()
        game_ids = list(set(game_ids))
        stats2 = cur2NCAA.fetchall()
        db.close()
        if(len(stats2) > 0):
            result = pd.DataFrame(stats2)
            result.index = result[0]
            resultsNCAA = []
            timesNCAA = []
            for i in range (0, len(game_ids)):
                result2 = result.ix[game_ids[i][0]]
                teams = result2[1]
                result2 = result2.transpose()
                result2.columns = teams
                result2 = result2.ix[2:13]
                result2.index = ['FGM-A', 'TPM-A', 'FTM-A', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'PTS']
                resultsNCAA.append(result2)
                timesNCAA.append(game_ids[i][1])
    if len(stats) > 0 and len(stats2) > 0:
        return render_template('index.html', resultsNCF=resultsNCF, timesNCF=timesNCF, resultsNCAA=resultsNCAA, timesNCAA=timesNCAA)
    elif len(stats) == 0 and len(stats2) > 0:
        return render_template('index.html', resultsNCAA=resultsNCAA, timesNCAA=timesNCAA)
    elif len(stats) > 0 and len(stats2) == 0:
        return render_template('index.html', resultsNCF=resultsNCF, timesNCF=timesNCF)
    else:
        return render_template('index.html', error='No Box Scores')

if __name__ == '__main__':
    application.run(host='0.0.0.0')
#    application.run()
