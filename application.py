import os
import sqlite3
import pandas as pd
from flask import render_template
from flask import g
from flask import Flask

#DATABASE = '~/Downloads/sports'

application = Flask(__name__)
application.debug = True

application.config.update(dict(
    DATABASE='/home/ec2-user/sports/sports.db',
#    DATABASE='/Users/tanyacashorali/Documents/Scripts/sports/sports.db',
    DEBUG=True
    #SECRET_KEY='development key',
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

@application.route('/')
def show_entries():
    with application.app_context():
        db = get_db()
        cur = db.execute('select game_id, game_date FROM games')
        cur2 = db.execute('select * FROM stats')
        game_ids = cur.fetchall()
        stats = cur2.fetchall()
        db.close()
        if(len(stats) > 0):
   	    result = pd.DataFrame(stats)
            result.index = result[0]
            results = []
            times = []
	    for i in range (0, len(game_ids)):
                result = result.ix[game_ids[i][0]]
                teams = result[1]
                result = result.transpose()
                result.columns = teams
                result = result.ix[2:]
                result.index = ['First Downs', 'Third Downs', 'Fourth Downs', 'Total Yards', 'Passing', 'Completion Attempts', 'Rushing', 'Rushing Attempts', 'Yards Per Pass', 'Yards Per Rush', 'Penalties', 'Turnovers', \
'Fumbles Lost', 'Ints Thrown', 'Possession']    
                results.append(result)
                times.append(game_ids[i][1])
        else:
	    return(render_template('index.html', error='No Box Scores'))
        return render_template('index.html', results=results, times=times)

if __name__ == '__main__':
    application.run(host='0.0.0.0')
