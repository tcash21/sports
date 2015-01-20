--create database 'sports.db';
attach database 'sports.db' as 'sports';

create table sports.games(
        game_id INT PRIMARY KEY NOT NULL,
        team1 CHAR(5) NOT NULL,
        team2 CHAR(5) NOT NULL,
        game_date TEXT NOT NULL
);

create table sports.stats(
		game_id INT NOT NULL,
		team CHAR(5) NOT NULL,
		first_downs INT NOT NULL,
		third_downs TEXT NOT NULL,
		fourth_downs TEXT NOT NULL,
		total_yards INT NOT NULL,
		passing INT NOT NULL,
		comp_att TEXT NOT NULL,
		yards_per_pass NUMERIC NOT NULL,
		rushing INT NOT NULL,
		rushing_attempts INT NOT NULL,
		yards_per_rush NUMERIC NOT NULL,
		penalties TEXT NOT NULL,
		turnovers INT NOT NULL,
		fumbles_lost INT NOT NULL,
		ints_thrown INT NOT NULL,
		possession TEXT NOT NULL
);

CREATE TABLE NCAAseasonstats(
		team CHAR(5) NOT NULL,
		the_date TEXT INT NOT NULL,
		min TEXT NOT NULL,
		fgm INT NOT NULL,
		fga INT NOT NULL,
		ftm INT NOT NULL,
		fta INT NOT NULL,
		tpm INT NOT NULL,
		tpa INT NOT NULL,
		pts INT NOT NULL,
		offr INT NOT NULL,
		defr INT NOT NULL,
		reb INT NOT NULL,
		ast INT NOT NULL,
		turnovers INT NOT NULL,
		stl INT NOT NULL,
                blk INT NOT NULL,
 		PRIMARY KEY (team, the_date)
);

CREATE TABLE NCAAstats(
    game_id INT NOT NULL,
    team CHAR(5) NOT NULL,
    fgma TEXT NOT NULL,
    tpma TEXT NOT NULL,
    ftma TEXT NOT NULL,
    oreb INT NOT NULL,
    dreb INT NOT NULL,
    reb INT NOT NULL,
    ast NUMERIC NOT NULL,
    stl INT NOT NULL,
    blk INT NOT NULL,
    turnovers INT NOT NULL,
    pf INT NOT NULL,
    pts INT NOT NULL
);

CREATE TABLE NCAAgames(
        game_id INT PRIMARY KEY NOT NULL,
        team1 CHAR(5) NOT NULL,
        team2 CHAR(5) NOT NULL,
        game_date TEXT NOT NULL
);

CREATE TABLE NCAAlines(
	away_team CHAR(40) NOT NULL,
	home_team CHAR(40) NOT NULL,
	line CHAR(10) NOT NULL,
	spread CHAR(10) NOT NULL,
	game_date TEXT NOT NULL,
 	game_time TEXT NOT NULL,
	PRIMARY KEY (away_team, home_team, game_date, line, spread)
);

CREATE TABLE NCAAHalflines(
        away_team CHAR(40) NOT NULL,
        home_team CHAR(40) NOT NULL,
        line CHAR(10) NOT NULL,
        spread CHAR(10) NOT NULL,
        game_date TEXT NOT NULL,
        game_time TEXT NOT NULL,
        PRIMARY KEY (away_team, home_team, game_date, line, spread)
);

CREATE TABLE NCAAteamlookup(
	covers_team CHAR(40) NOT NULL,
	espn_abbr CHAR(5),
	PRIMARY KEY (covers_team)
);
