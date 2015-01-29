library(RSQLite)

drv <- dbDriver("SQLite")
con <- dbConnect(drv, "/home/ec2-user/sports/sports.db")

tables <- dbListTables(con)

lDataFrames <- vector("list", length=length(tables))

## create a data.frame for each table
for (i in seq(along=tables)) {
  if(tables[[i]] == 'NCAAHalflines' | tables[[i]] == 'NCAAlines'){
  lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT away_team, home_team, max(game_time) from ", tables[[i]], " group by away_team, home_team;"))
  } else {
  	lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[i]], "'", sep=""))
  }
  cat(tables[[i]], "\n")
}

halflines <- lDataFrames[[1]]
games <- lDataFrames[[2]]
lines <- lDataFrames[[3]]
teamstats <- lDataFrames[[4]]
boxscores <- lDataFrames[[5]]
lookup <- lDataFrames[[6]]

m1<-merge(boxscores, games, by="game_id")
m1$key <- paste(m1$team, m1$game_date)
teamstats$key <- paste(teamstats$team, teamstats$the_date)
m2<-merge(m1, teamstats, by="key")
lookup$away_team <- lookup$covers_team
lookup$home_team <- lookup$covers_team
la<-merge(lookup, lines, by="away_team")
lh<-merge(lookup, lines, by="home_team")
la$key <- paste(la$espn_abbr, la$game_date)
lh$key <- paste(lh$espn_abbr, lh$game_date)
m3a<-merge(m2, la, by="key")
m3h<-merge(m2, lh, by="key")
colnames(m3h)[39:40] <- c("home_team.x", "home_team.y")
colnames(m3a)[36] <- "home_team"
all <- all[,-1]
all$key <- paste(all$game_id, all$team.y)
all<-all[match(unique(all$key), all$key),]
