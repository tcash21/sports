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
