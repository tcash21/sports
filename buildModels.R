library(plyr)
library(RSQLite)
library(sendmailR)

drv <- dbDriver("SQLite")
con <- dbConnect(drv, "/home/ec2-user/sports/sports.db")

tables <- dbListTables(con)

lDataFrames <- vector("list", length=length(tables))

## create a data.frame for each table
for (i in seq(along=tables)) {
  if(tables[[i]] == 'NCAAHalflines' | tables[[i]] == 'NCAAlines'){
  lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT away_team, home_team, game_date, line, spread, max(game_time) as 
game_time from ", tables[[i]], " group by away_team, home_team, game_date;"))
  } else {
  	lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[i]], "'", sep=""))
  }
  cat(tables[[i]], ":", i, "\n")
}

halflines <- lDataFrames[[9]]
games <- lDataFrames[[11]]
lines <- lDataFrames[[12]]
teamstats <- lDataFrames[[13]]
boxscores <- lDataFrames[[15]]
lookup <- lDataFrames[[16]]
ncaafinal <- lDataFrames[[10]]
seasontotals <- lDataFrames[[14]]

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


colnames(m3h)[44:45] <- c("home_team.x", "home_team.y")
colnames(m3a)[41] <- "home_team"
#all <- rbind(m3a, m3h)


halftime_stats<-rbind(m3a,m3h)
halftime_stats <- subset(halftime_stats, line.y != 'OFF')
halftime_stats<-halftime_stats[order(halftime_stats$game_id),]
diffs<-ddply(halftime_stats, .(game_id), transform, diff=pts.x - pts.x[1])
halftime_stats$half_diff <- diffs$diff
halftime_stats$line.y<-as.numeric(halftime_stats$line.y)
halftime_stats$line <- as.numeric(halftime_stats$line)
mwt <- ddply(halftime_stats, .(game_id), transform, mwt=pts.x + pts.x[1] + line.y - line)


## removes any anomalies or games with != 2 game_ids
mwt <- mwt[-which(mwt$game_id %in% names(which(table(mwt$game_id) != 2))),]
half_stats<-mwt[seq(from=2, to=dim(mwt)[1], by=2),]

#colnames(m3h)[44:45] <- c("home_team.x", "home_team.y")
#colnames(m3a)[41] <- "home_team"
all <- rbind(m3a, m3h)
all <- all[,-1]
all$key <- paste(all$game_id, all$team.y)
all<-all[match(unique(all$key), all$key),]

#final<-merge(ncaafinal, all, by="key")

colnames(all) <- c("GAME_ID","TEAM","HALF_FGM", "HALF_FGA", "HALF_3PM", 
"HALF_3PA", "HALF_FTM","HALF_FTA","HALF_OREB", "HALF_DREB", "HALF_REB", "HALF_AST", "HALF_STL", "HALF_BLK", "HALF_TO", "HALF_PF", "HALF_PTS",
"HALF_TIMESTAMP", "TEAM1", "TEAM2", "GAME_DATE","GAME_TIME","REMOVE2","REMOVE3","MIN", "SEASON_FGM","SEASON_FGA","SEASON_FTM","SEASON_FTA","SEASON_3PM",
"SEASON_3PA","SEASON_PTS","SEASON_OFFR","SEASON_DEFR","SEASON_REB","SEASON_AST","SEASON_TO","SEASON_STL", "SEASON_BLK","REMOVE4","REMOVE5","REMOVE6",
"REMOVE7","REMOVE8","REMOVE9","LINE", "SPREAD", "COVERS_UPDATE","LINE_HALF", "SPREAD_HALF", "COVERS_HALF_UPDATE")
all <- all[,-grep("REMOVE", colnames(all))]

## Add the season total stats
colnames(seasontotals)[1] <- "TEAM"
colnames(seasontotals)[2] <- "GAME_DATE"
#today <- format(Sys.Date(), "%m/%d/%Y")
#seasontotals <- subset(seasontotals, GAME_DATE == today)
all$key <- paste(all$GAME_DATE, all$TEAM)
seasontotals$key <- paste(seasontotals$GAME_DATE, seasontotals$TEAM)

x<-merge(seasontotals, all, by=c("key"))
x<- x[,c(-1, -5, -16, -35)]
final<-x[,c(1:53)]
colnames(final)[3:12] <- c("SEASON_GP", "SEASON_PPG", "SEASON_RPG", "SEASON_APG", "SEASON_SPG", "SEASON_BPG", "SEASON_TPG", "SEASON_FGP", 
"SEASON_FTP", "SEASON_3PP")
#final$GAME_DATE <- seasontotals$GAME_DATE[1]
#final$GAME_DATE<-games[match(final$GAME_ID, games$game_id),]$game_date
final<-final[order(final$GAME_DATE, decreasing=TRUE),]

## match half stats that have 2nd half lines with final set
f<-final[which(final$GAME_ID %in% half_stats$game_id),]
f$mwt <- half_stats[match(f$GAME_ID, half_stats$game_id),]$mwt
f$half_diff <- half_stats[match(f$GAME_ID, half_stats$game_id),]$half_diff
f[,3:12] <- apply(f[,3:12], 2, function(x) as.numeric(as.character(x)))
f[,14:28] <- apply(f[,14:28], 2, function(x) as.numeric(as.character(x)))
f[,34:49] <- apply(f[,34:49], 2, function(x) as.numeric(as.character(x)))
f[,51:52] <- apply(f[,51:52], 2, function(x) as.numeric(as.character(x)))

## Team1 and Team2 Halftime Differentials
f$fg_percent <- ((f$HALF_FGM / f$HALF_FGA) - (f$SEASON_FGM / f$SEASON_FGA - 1.0))
f$FGM <- (f$HALF_FGM - (f$SEASON_FGM / f$SEASON_GP / 2))
f$TPM <- (f$HALF_3PM - (f$SEASON_3PM / f$SEASON_GP / 2))
f$FTM <- (f$HALF_FTM - (f$SEASON_FTM / f$SEASON_GP / 2 - 1))
f$TO <- (f$HALF_TO - (f$SEASON_TO / f$SEASON_GP / 2))
f$OREB <- (f$HALF_OREB - (f$SEASON_OFFR / f$SEASON_GP / 2))

## Cumulative Halftime Differentials
f$chd_fg <- ddply(f, .(GAME_ID), transform, chd_fg = (fg_percent + fg_percent[1]) / 2)$chd_fg
f$chd_fgm <- ddply(f, .(GAME_ID), transform, chd_fgm = (FGM + FGM[1]) / 2)$chd_fgm
f$chd_tpm <- ddply(f, .(GAME_ID), transform, chd_tpm = (TPM + TPM[1]) / 2)$chd_tpm
f$chd_ftm <- ddply(f, .(GAME_ID), transform, chd_ftm = (FTM + FTM[1]) / 2)$chd_ftm
f$chd_to <- ddply(f, .(GAME_ID), transform, chd_to = (TO + TO[1]) / 2)$chd_to
f$chd_oreb <- ddply(f, .(GAME_ID), transform, chd_oreb = (OREB + OREB[1]) / 2)$chd_oreb

write.csv(f, file="/home/ec2-user/sports/modelStats.csv", row.names=FALSE)

sendmailV <- Vectorize( sendmail , vectorize.args = "to" )
#emails <- c( "<tanyacash@gmail.com>" , "<malloyc@yahoo.com>", "<sschopen@gmail.com>")
emails <- c("<tanyacash@gmail.com>")

from <- "<tanyacash@gmail.com>"
subject <- "Weekly NCAA Data Report"
body <- c(
  "Chris -- see the attached file.",
  mime_part("/home/ec2-user/sports/modelStats.csv", "WeeklyData.csv")
)
sendmailV(from, to=emails, subject, body)

