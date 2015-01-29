library(RSQLite)
library(mailR)

drv <- dbDriver("SQLite")
con <- dbConnect(drv, "/home/ec2-user/sports/sports.db")

tables <- dbListTables(con)

lDataFrames <- vector("list", length=length(tables))

## create a data.frame for each table
for (i in seq(along=tables)) {
  if(tables[[i]] == 'NCAAHalflines' | tables[[i]] == 'NCAAlines'){
  lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT away_team, home_team, game_date, line, spread, max(game_time) as game_time from ", tables[[i]], " group by away_team, home_team, game_date;"))
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

## Total Lines
la<-merge(lookup, lines, by="away_team")
lh<-merge(lookup, lines, by="home_team")
la$key <- paste(la$espn_abbr, la$game_date)
lh$key <- paste(lh$espn_abbr, lh$game_date)
m3a<-merge(m2, la, by="key")
m3h<-merge(m2, lh, by="key")
colnames(m3a)[44] <- "CoversTotalLineUpdateTime"
colnames(m3h)[44] <- "CoversTotalLineUpdateTime"

## Halftime Lines
la2<-merge(lookup, halflines, by="away_team")
lh2<-merge(lookup, halflines, by="home_team")
la2$key <- paste(la2$espn_abbr, la2$game_date)
lh2$key <- paste(lh2$espn_abbr, lh2$game_date)
m3a2<-merge(m2, la2, by="key")
m3h2<-merge(m2, lh2, by="key")
colnames(m3a2)[44] <- "CoversHalfLineUpdateTime"
colnames(m3h2)[44] <- "CoversHalfLineUpdateTime"

l<-merge(m3a, m3a2, by=c("game_date.y", "away_team"))
m3a<-cbind(m3a, l[,84:86])
l2<-merge(m3h, m3h2, by=c("game_date.y", "home_team"))
m3h<-cbind(m3h, l2[,84:86])

colnames(m3h)[39:40] <- c("home_team.x", "home_team.y")
colnames(m3a)[36] <- "home_team"
all <- rbind(m3a, m3h)
all <- all[,-1]
all$key <- paste(all$game_id, all$team.y)
all<-all[match(unique(all$key), all$key),]

colnames(all) <- c("GAME_ID","TEAM","FGM-A","3PM-A","FTM-A","OREB","DREB","REB","AST","STL","BLK","TO","PF","PTS","TEAM1","TEAM2","GAME_DATE","REMOVE1","REMOVE2","REMOVE3","SEASON_FGM","SEASON_FGA","SEASON_FTM","SEASON_FTA","SEASON_3PM","SEASON_3PA","SEASON_PTS","SEASON_OFFR","SEASON_DEFR","SEASON_REB","SEASON_AST","SEASON_TO","SEASON_STL","SEASON_BLK","REMOVE4","REMOVE5","REMOVE6","REMOVE7","REMOVE8","REMOVE9","LINE", "SPREAD", "COVERS_UPDATE","LINE_HALF", "SPREAD_HALF", "COVERS_HALF_UPDATE", "REMOVE11")
all <- all[,-grep("REMOVE", colnames(all))]

write.csv(all, file="testfile.csv", row.names=FALSE)

sender <- "tanyacash@gmail.com" # Replace with a valid address
recipients <- c("tanyacash@gmail.com") # Replace with one or more valid addresses
email <- send.mail(from = sender,
to = recipients,
subject="Subject of the email",
body = "Body of the email",
smtp = list(host.name = "aspmx.l.google.com", port = 25),
authenticate = FALSE,
attach.files = c("/home/ec2-user/testfile.csv"),
send = FALSE)
email$send() # execute to send email


