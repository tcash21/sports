library(RSQLite)
library(sendmailR)

drv <- dbDriver("SQLite")
con <- dbConnect(drv, "/home/ec2-user/sports/sports.db")

tables <- dbListTables(con)

lDataFrames <- vector("list", length=length(tables))

## create a data.frame for each table
for (i in seq(along=tables)) {
  if(tables[[i]] == 'NBAHalflines' | tables[[i]] == 'NBAlines'){
  lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT away_team, home_team, game_date, line, spread, max(game_time) as 
game_time from ", tables[[i]], " group by away_team, home_team, game_date;"))
  } else {
  	lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[i]], "'", sep=""))
  }
  cat(tables[[i]], ":", i, "\n")
}

halflines <- lDataFrames[[1]]
games <- lDataFrames[[3]]
lines <- lDataFrames[[4]]
teamstats <- lDataFrames[[5]]
boxscores <- lDataFrames[[7]]
lookup <- lDataFrames[[8]]
nbafinal <- lDataFrames[[2]]
seasontotals <- lDataFrames[[6]]

b<-apply(boxscores[,3:5], 2, function(x) strsplit(x, "-"))
boxscores$fgm <- do.call("rbind",b$fgma)[,1]
boxscores$fga <- do.call("rbind",b$fgma)[,2]
boxscores$tpm <- do.call("rbind",b$tpma)[,1]
boxscores$tpa <- do.call("rbind",b$tpma)[,2]
boxscores$ftm <- do.call("rbind",b$ftma)[,1]
boxscores$fta <- do.call("rbind",b$ftma)[,2]
boxscores <- boxscores[,c(1,2,16:21,6:15)]

m1<-merge(boxscores, games, by="game_id")
m1$key <- paste(m1$team, m1$game_date)
teamstats$team<-lookup[match(teamstats$team, lookup$espn_name),]$espn_abbr
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
colnames(m3a)[49] <- "CoversTotalLineUpdateTime"
colnames(m3h)[49] <- "CoversTotalLineUpdateTime"

## Halftime Lines
la2<-merge(lookup, halflines, by="away_team")
lh2<-merge(lookup, halflines, by="home_team")
la2$key <- paste(la2$espn_abbr, la2$game_date)
lh2$key <- paste(lh2$espn_abbr, lh2$game_date)
m3a2<-merge(m2, la2, by="key")
m3h2<-merge(m2, lh2, by="key")
colnames(m3a2)[49] <- "CoversHalfLineUpdateTime"
colnames(m3h2)[49] <- "CoversHalfLineUpdateTime"

l<-merge(m3a, m3a2, by=c("game_date.y", "away_team"))
l<-l[match(m3a$key, l$key.y),]
m3a<-cbind(m3a, l[,94:96])
l2<-merge(m3h, m3h2, by=c("game_date.y", "home_team"))
l2<-l2[match(m3h$key, l2$key.y),]
m3h<-cbind(m3h, l2[,94:96])

nbafinal$key <- paste(nbafinal$game_id, nbafinal$team)
n<-apply(nbafinal[,3:5], 2, function(x) strsplit(x, "-"))
nbafinal$fgm <- do.call("rbind",n$fgma)[,1]
nbafinal$fga <- do.call("rbind",n$fgma)[,2]
nbafinal$tpm <- do.call("rbind",n$tpma)[,1]
nbafinal$tpa <- do.call("rbind",n$tpma)[,2]
nbafinal$ftm <- do.call("rbind",n$ftma)[,1]
nbafinal$fta <- do.call("rbind",n$ftma)[,2]
nbafinal <- nbafinal[,c(1,2,17:22,6:16)]

colnames(m3h)[44:45] <- c("home_team.x", "home_team.y")
colnames(m3a)[40] <- "home_team"
all <- rbind(m3a, m3h)
all <- all[,-1]
all$key <- paste(all$game_id, all$team.y)
all<-all[match(unique(all$key), all$key),]

final<-merge(nbafinal, all, by="key")
final <- final[,-1]

colnames(final) <- c("GAME_ID","TEAM","FINAL_FGM","FINAL_FGA", "FINAL_3PM","FINAL_3PA","FINAL_FTM","FINAL_FTA","FINAL_OREB","FINAL_DREB","FINAL_REB",
"FINAL_AST","FINAL_STL","FINAL_BLK","FINAL_TO","FINAL_PF","FINAL_PTS","FINAL_BOXSCORE_TIMESTAMP", "REMOVE0","REMOVE1","HALF_FGM", "HALF_FGA", "HALF_3PM", 
"HALF_3PA", "HALF_FTM","HALF_FTA","HALF_OREB", "HALF_DREB", "HALF_REB", "HALF_AST", "HALF_STL", "HALF_BLK", "HALF_TO", "HALF_PF", "HALF_PTS",
"HALF_TIMESTAMP", "TEAM1", "TEAM2", "GAME_DATE","GAME_TIME","REMOVE2","REMOVE3", "SEASON_FGM","SEASON_FGA","SEASON_FG%", "SEASON_3PM", "SEASON_3PA","SEASON_3P%", 
"SEASON_FTM","SEASON_FTA","SEASON_FT%","SEASON_2PM", "SEASON_2PA", "SEASON_2P%", "SEASON_PPS", "SEASON_AFG", "REMOVE4","REMOVE5","REMOVE6","REMOVE7","REMOVE8","REMOVE9",
"REMOVE10", "LINE", "SPREAD", "COVERS_UPDATE","LINE_HALF", "SPREAD_HALF", "COVERS_HALF_UPDATE")
final <- final[,-grep("REMOVE", colnames(final))]

## Add the season total stats
colnames(seasontotals)[1] <- "TEAM"
colnames(seasontotals)[2] <- "GAME_DATE"
#today <- format(Sys.Date(), "%m/%d/%Y")
#seasontotals <- subset(seasontotals, GAME_DATE == today)
final$key <- paste(final$GAME_DATE, final$TEAM)
seasontotals$TEAM<-lookup[match(seasontotals$TEAM, lookup$espn_name),]$espn_abbr
seasontotals$key <- paste(seasontotals$GAME_DATE, seasontotals$TEAM)

x<-merge(seasontotals, final, by=c("key"))
x<- x[,c(-1, -16, -51)]
final<-x[,c(14:46, 1:13, 47:69)]
colnames(final)[36:46] <- c("SEASON_GP", "SEASON_PPG", "SEASON_ORPG", "SEASON_DEFR", "SEASON_RPG", "SEASON_APG", "SEASON_SPG", 
"SEASON_BPG", "SEASON_TPG", "SEASON_FPG", "SEASON_ATO")
#final$GAME_DATE <- seasontotals$GAME_DATE[1]
#final$GAME_DATE<-games[match(final$GAME_ID, games$game_id),]$game_date
final<-final[order(final$GAME_DATE, decreasing=TRUE),]

write.csv(final, file="/home/ec2-user/sports/testfile.csv", row.names=FALSE)

sendmailV <- Vectorize( sendmail , vectorize.args = "to" )
emails <- c( "<tanyacash@gmail.com>" , "<malloyc@yahoo.com>", "<sschopen@gmail.com>")
#emails <- c("<tanyacash@gmail.com>")

from <- "<tanyacash@gmail.com>"
subject <- "Weekly NBA Data Report"
body <- c(
  "Chris -- see the attached file.",
  mime_part("/home/ec2-user/sports/testfile.csv", "WeeklyData.csv")
)
sendmailV(from, to=emails, subject, body)

