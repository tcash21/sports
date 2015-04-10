library(RSQLite)
library(sendmailR)
library(plyr)

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

halflines <- lDataFrames[[12]]
games <- lDataFrames[[17]]
lines <- lDataFrames[[18]]
teamstats <- lDataFrames[[19]]
boxscores <- lDataFrames[[21]]
lookup <- lDataFrames[[22]]
ncaafinal <- lDataFrames[[16]]
seasontotals <- lDataFrames[[20]]
papg <- lDataFrames[[24]]


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

ncaafinal$key <- paste(ncaafinal$game_id, ncaafinal$team)
n<-apply(ncaafinal[,3:5], 2, function(x) strsplit(x, "-"))
ncaafinal$fgm <- do.call("rbind",n$fgma)[,1]
ncaafinal$fga <- do.call("rbind",n$fgma)[,2]
ncaafinal$tpm <- do.call("rbind",n$tpma)[,1]
ncaafinal$tpa <- do.call("rbind",n$tpma)[,2]
ncaafinal$ftm <- do.call("rbind",n$ftma)[,1]
ncaafinal$fta <- do.call("rbind",n$ftma)[,2]
ncaafinal <- ncaafinal[,c(1,2,17:22,6:16)]

colnames(m3h)[44:45] <- c("home_team.x", "home_team.y")
colnames(m3a)[41] <- "home_team"
all <- rbind(m3a, m3h)
all <- all[,-1]
all$key <- paste(all$game_id, all$team.y)
all<-all[match(unique(all$key), all$key),]

final<-merge(ncaafinal, all, by="key")
final <- final[,-1]

colnames(final) <- c("GAME_ID","TEAM","FINAL_FGM","FINAL_FGA", "FINAL_3PM","FINAL_3PA","FINAL_FTM","FINAL_FTA","FINAL_OREB","FINAL_DREB","FINAL_REB",
"FINAL_AST","FINAL_STL","FINAL_BLK","FINAL_TO","FINAL_PF","FINAL_PTS","FINAL_BOXSCORE_TIMESTAMP", "REMOVE0","REMOVE1","HALF_FGM", "HALF_FGA", "HALF_3PM", 
"HALF_3PA", "HALF_FTM","HALF_FTA","HALF_OREB", "HALF_DREB", "HALF_REB", "HALF_AST", "HALF_STL", "HALF_BLK", "HALF_TO", "HALF_PF", "HALF_PTS",
"HALF_TIMESTAMP", "TEAM1", "TEAM2", "GAME_DATE","GAME_TIME","REMOVE2","REMOVE3","MIN", "SEASON_FGM","SEASON_FGA","SEASON_FTM","SEASON_FTA","SEASON_3PM",
"SEASON_3PA","SEASON_PTS","SEASON_OFFR","SEASON_DEFR","SEASON_REB","SEASON_AST","SEASON_TO","SEASON_STL", "SEASON_BLK","REMOVE4","REMOVE5","REMOVE6",
"REMOVE7","REMOVE8","REMOVE9","LINE", "SPREAD", "COVERS_UPDATE","LINE_HALF", "SPREAD_HALF", "COVERS_HALF_UPDATE")
final <- final[,-grep("REMOVE", colnames(final))]

## Add the season total stats
colnames(seasontotals)[1] <- "TEAM"
colnames(seasontotals)[2] <- "GAME_DATE"
#today <- format(Sys.Date(), "%m/%d/%Y")
#seasontotals <- subset(seasontotals, GAME_DATE == today)
final$key <- paste(final$GAME_DATE, final$TEAM)
seasontotals$key <- paste(seasontotals$GAME_DATE, seasontotals$TEAM)

x<-merge(seasontotals, final, by=c("key"))
x<- x[,c(-1, -16, -51)]
final<-x[,c(14:51, 1:3,5:13, 52:70)]
colnames(final)[41:50] <- c("SEASON_GP", "SEASON_PPG", "SEASON_RPG", "SEASON_APG", "SEASON_SPG", "SEASON_BPG", "SEASON_TPG", "SEASON_FGP", 
"SEASON_FTP", "SEASON_3PP")
#final$GAME_DATE <- seasontotals$GAME_DATE[1]
#final$GAME_DATE<-games[match(final$GAME_ID, games$game_id),]$game_date
final<-final[order(final$GAME_DATE, decreasing=TRUE),]

#final <- subset(final, LINE_HALF != "OFF")
final$LINE_HALF <- as.numeric(final$LINE_HALF)
final$LINE <- as.numeric(final$LINE)
final$COVERS_UPDATE<-as.character(final$COVERS_UPDATE)
final<-ddply(final, .(GAME_ID), transform, mwt=HALF_PTS[1] + HALF_PTS[2] + LINE_HALF - LINE)
final <- ddply(final, .(GAME_ID), transform, half_diff=HALF_PTS[1] - HALF_PTS[2])

## transform to numerics
final[,2:16]<-apply(final[,2:16], 2, as.numeric)
final[,18:32]<-apply(final[,18:32], 2, as.numeric)
final[,c(38,41:63)]<-apply(final[,c(38,41:63)], 2, as.numeric)


## Team1 and Team2 Halftime Differentials
final$fg_percent <- ((final$HALF_FGM / final$HALF_FGA) - (final$SEASON_FGM / final$SEASON_FGA) - .01)
final$fg_percent_noadjustment <- (final$HALF_FGM / final$HALF_FGA) - (final$SEASON_FGM / final$SEASON_FGA)
final$FGM <- (final$HALF_FGM - (final$SEASON_FGM / final$SEASON_GP / 2))
final$TPM <- (final$HALF_3PM - (final$SEASON_3PM / final$SEASON_GP / 2))
final$FTM <- (final$HALF_FTM - (final$SEASON_FTM / final$SEASON_GP / 2 - 1))
final$TO <- (final$HALF_TO - (final$SEASON_TO / final$SEASON_GP / 2))
final$OREB <- (final$HALF_OREB - (final$SEASON_OFFR / final$SEASON_GP / 2))

## Cumulative Halftime Differentials
final$chd_fg <- ddply(final, .(GAME_ID), transform, chd_fg = (fg_percent[1] + fg_percent[2]) / 2)$chd_fg
final$chd_fgm <- ddply(final, .(GAME_ID), transform, chd_fgm = (FGM[1] + FGM[2]) / 2)$chd_fgm
final$chd_tpm <- ddply(final, .(GAME_ID), transform, chd_tpm = (TPM[1] + TPM[2]) / 2)$chd_tpm
final$chd_ftm <- ddply(final, .(GAME_ID), transform, chd_ftm = (FTM[1] + FTM[2]) / 2)$chd_ftm
final$chd_to <- ddply(final, .(GAME_ID), transform, chd_to = (TO[1] + TO[1]) / 2)$chd_to
final$chd_oreb <- ddply(final, .(GAME_ID), transform, chd_oreb = (OREB[1] + OREB[2]) / 2)$chd_oreb

## Add Criteria for Over/Under
result <- final
result$mwtO <- as.numeric(result$mwt < 7.1 & result$mwt > -3.9)
result$chd_fgO <- as.numeric(result$chd_fg < .15 & result$chd_fg > -.07)
result$chd_fgmO <- as.numeric(result$chd_fgm < -3.9)
result$chd_tpmO <- as.numeric(result$chd_tpm < -1.9)
result$chd_ftmO <- as.numeric(result$chd_ftm < -.9)
result$chd_toO <- as.numeric(result$chd_to < -1.9)

result$mwtO[is.na(result$mwtO)] <- 0
result$chd_fgO[is.na(result$chd_fgO)] <- 0
result$chd_fgmO[is.na(result$chd_fgmO)] <- 0
result$chd_tpmO[is.na(result$chd_tpmO)] <- 0
result$chd_ftmO[is.na(result$chd_ftmO)] <- 0
result$chd_toO[is.na(result$chd_toO)] <- 0
result$overSum <- result$mwtO + result$chd_fgO + result$chd_fgmO + result$chd_tpmO + result$chd_ftmO + result$chd_toO

result$fullSpreadU <- as.numeric(abs(as.numeric(result$SPREAD)) > 10.9)
result$mwtU <- as.numeric(result$mwt > 7.1)
result$chd_fgU <- as.numeric(result$chd_fg > .15 | result$chd_fg < -.07)
result$chd_fgmU <- 0
result$chd_tpmU <- 0
result$chd_ftmU <- as.numeric(result$chd_ftm > -0.9)
result$chd_toU <- as.numeric(result$chd_to > -1.9)

result$mwtU[is.na(result$mwtU)] <- 0
result$chd_fgO[is.na(result$chd_fgU)] <- 0
result$chd_fgmU[is.na(result$chd_fgmU)] <- 0
result$chd_tpmU[is.na(result$chd_tpmU)] <- 0
result$chd_ftmU[is.na(result$chd_ftmU)] <- 0
result$chd_toU[is.na(result$chd_toU)] <- 0
result$underSum <- result$fullSpreadU + result$mwtU + result$chd_fgU + result$chd_fgmU + result$chd_tpmU + result$chd_ftmU + result$chd_toU

#result <- subset(result, !is.na(LINE_HALF))
result$SECOND_HALF_PTS <- result$FINAL_PTS - result$HALF_PTS
result$Over<- ddply(result, .(GAME_ID), transform, over=sum(SECOND_HALF_PTS) > LINE_HALF)$over
#fill <- which(is.na(result$underSum) | is.na(result$overSum) | is.na(result$LINE_HALF))
#train <- result[-which(is.na(result$underSum) | is.na(result$overSum) | is.na(result$LINE_HALF)),]
#result$overPred <- ""
#r <- randomForest(formula = as.factor(Over) ~ underSum * overSum * LINE_HALF, data = train)
#result$overPred[fill] <- "NA"

#save(r, file="~/sports/randomForestModel.Rdat")


write.csv(result, file="/home/ec2-user/sports/testfile.csv", row.names=FALSE)

sendmailV <- Vectorize( sendmail , vectorize.args = "to" )
emails <- c( "<tanyacash@gmail.com>" , "<malloyc@yahoo.com>", "<sschopen@gmail.com>")
#emails <- c("<tanyacash@gmail.com>")

from <- "<tanyacash@gmail.com>"
subject <- "NCAA Data - all data"
body <- c(
  "Chris -- see the attached file.",
  mime_part("/home/ec2-user/sports/testfile.csv", "allData.csv")
)
sendmailV(from, to=emails, subject, body)




