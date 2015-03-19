library(reshape)
library(plyr)
library(RSQLite)
library(shiny)
library(rCharts)


drv <- dbDriver("SQLite")
con <- dbConnect(drv, "/home/ec2-user/sports/sports.db")

tables <- dbListTables(con)

lDataFrames <- vector("list", length=length(tables))
 

 ## create a data.frame for each table
for (i in seq(along=tables)) {
  if(tables[[i]] == 'NCAAHalflines' | tables[[i]] == 'NCAAlines'){
     #lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste0("SELECT n.away_team, n.home_team, n.game_date, n.line, n.spread, n.game_time from '", tables[[i]], "' n inner join 
     #(select game_date, away_team,home_team, max(game_time) as mgt from '", tables[[i]], "' group by game_date, away_team, home_team) s2 on s2.game_date = n.game_date and 
     # s2.away_team = n.away_team and s2.home_team = n.home_team and n.game_time = s2.mgt;"))
     lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste0("SELECT * FROM '", tables[[i]], "'"))
  } else {
      lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[i]], "'",sep=""))
  }
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
lines$game_time<-as.POSIXlt(lines$game_time)
lines<-lines[order(lines$home_team, lines$game_time),]
lines$key <- paste(lines$away_team, lines$home_team, lines$game_date)
res2 <- tapply(1:nrow(lines), INDEX=lines$key, FUN=function(idxs) idxs[lines[idxs,'line'] != 'OFF'][1])
first<-lines[res2[which(!is.na(res2))],]
lines <- first[,1:6]

## Merge line data with lookup table
la<-merge(lookup, lines, by="away_team")
lh<-merge(lookup, lines, by="home_team")
la$key <- paste(la$espn_abbr, la$game_date)
lh$key <- paste(lh$espn_abbr, lh$game_date)
m3a<-merge(m2, la, by="key")
m3h<-merge(m2, lh, by="key")
colnames(m3a)[49] <- "CoversTotalLineUpdateTime"
colnames(m3h)[49] <- "CoversTotalLineUpdateTime"

## Halftime Lines - use the first one after "OFF" for consistency
halflines$game_time<-as.POSIXlt(halflines$game_time)
halflines<-halflines[order(halflines$home_team, halflines$game_time),]
halflines$key <- paste(halflines$away_team, halflines$home_team, halflines$game_date)
res2 <- tapply(1:nrow(halflines), INDEX=halflines$key, FUN=function(idxs) idxs[halflines[idxs,'line'] != 'OFF'][1])
first<-halflines[res2[which(!is.na(res2))],]
halflines <- first[,1:6]

## Merge half lines with lookup table
la2<-merge(lookup, halflines, by="away_team")
lh2<-merge(lookup, halflines, by="home_team")
la2$key <- paste(la2$espn_abbr, la2$game_date)
lh2$key <- paste(lh2$espn_abbr, lh2$game_date)
m3a2<-merge(m2, la2, by="key")
m3h2<-merge(m2, lh2, by="key")
colnames(m3a2)[49] <- "CoversHalfLineUpdateTime"
colnames(m3h2)[49] <- "CoversHalfLineUpdateTime"

l<-merge(m3a, m3a2, by=c("key"))
#l<-l[match(m3a$key, l$key.y),]
m3a<-m3a[match(l$key, m3a$key),]
m3a<-cbind(m3a, l[,94:96])
l2<-merge(m3h, m3h2, by=c("key"))
m3h<-m3h[match(l2$key, m3h$key),]
m3h<-cbind(m3h, l2[,94:96])
colnames(m3h)[44:45] <- c("home_team.x", "home_team.y")
colnames(m3a)[41] <- "home_team"
#colnames(m3a)[54:55] <- c("away_team.x", "away_team.y")
#all <- rbind(m3a, m3h)
m3h <- m3h[,1:52]

halftime_stats<-rbind(m3a,m3h)
halftime_stats<-halftime_stats[-which(halftime_stats$game_id %in% names(which(table(halftime_stats$game_id) != 2)) ),]
#halftime_stats <- subset(halftime_stats, line.y != 'OFF')
halftime_stats<-halftime_stats[which(!is.na(halftime_stats$line.y)),]
halftime_stats<-halftime_stats[order(halftime_stats$game_id),]
halftime_stats$CoversTotalLineUpdateTime <- as.character(halftime_stats$CoversTotalLineUpdateTime)

diffs<-ddply(halftime_stats, .(game_id), transform, diff=pts.x[1] - pts.x[2])
halftime_stats$half_diff <- diffs$diff
halftime_stats$line.y<-as.numeric(halftime_stats$line.y)
halftime_stats$line <- as.numeric(halftime_stats$line)
mwt <- ddply(halftime_stats, .(game_id), transform, mwt=pts.x[1] + pts.x[2] + line.y - line)


## removes any anomalies or games with != 2 game_ids
if(length(which(mwt$game_id %in% names(which(table(mwt$game_id) != 2)))) > 0){
 
 mwt <- mwt[-which(mwt$game_id %in% names(which(table(mwt$game_id) != 2))),]
# half_stats<-mwt[seq(from=2, to=dim(mwt)[1], by=2),]
}

if(dim(mwt)[1] > 0){
half_stats <- mwt[seq(from=2, to=dim(mwt)[1], by=2),]
} else {
  return(data.frame(results="No Results"))
}
#colnames(m3h)[44:45] <- c("home_team.x", "home_team.y")
#colnames(m3a)[41] <- "home_team"
all <- rbind(m3a, m3h)
all <- all[,-1]
all$key <- paste(all$game_id, all$team.y)
all<-all[match(unique(all$key), all$key),]

colnames(all) <- c("GAME_ID","TEAM","HALF_FGM", "HALF_FGA", "HALF_3PM",
"HALF_3PA", "HALF_FTM","HALF_FTA","HALF_OREB", "HALF_DREB", "HALF_REB", "HALF_AST", "HALF_STL", "HALF_BLK", "HALF_TO", "HALF_PF", "HALF_PTS",
"HALF_TIMESTAMP", "TEAM1", "TEAM2", "GAME_DATE","GAME_TIME","REMOVE2","REMOVE3","MIN", "SEASON_FGM","SEASON_FGA","SEASON_FTM","SEASON_FTA","SEASON_3PM",
"SEASON_3PA","SEASON_PTS","SEASON_OFFR","SEASON_DEFR","SEASON_REB","SEASON_AST","SEASON_TO","SEASON_STL", "SEASON_BLK","REMOVE5","REMOVE6",
"REMOVE7","REMOVE8","REMOVE9","LINE", "SPREAD", "REMOVE12","COVERS_UPDATE","LINE_HALF", "SPREAD_HALF", "REMOVE10", "REMOVE11")
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
final<-x[,c(1:52)]
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
f$fg_percent <- ((f$HALF_FGM / f$HALF_FGA) - (f$SEASON_FGM / f$SEASON_FGA))
f$FGM <- (f$HALF_FGM - (f$SEASON_FGM / f$SEASON_GP / 2))
f$TPM <- (f$HALF_3PM - (f$SEASON_3PM / f$SEASON_GP / 2))
f$FTM <- (f$HALF_FTM - (f$SEASON_FTM / f$SEASON_GP / 2 - 1))
f$TO <- (f$HALF_TO - (f$SEASON_TO / f$SEASON_GP / 2))
f$OREB <- (f$HALF_OREB - (f$SEASON_OFFR / f$SEASON_GP / 2))

f$COVERS_UPDATE<-as.character(f$COVERS_UPDATE)

## Cumulative Halftime Differentials
f <- f[order(f$GAME_ID),]
f$chd_fg <- ddply(f, .(GAME_ID), transform, chd_fg = (fg_percent[1] + fg_percent[2]) / 2)$chd_fg
f$chd_fgm <- ddply(f, .(GAME_ID), transform, chd_fgm = (FGM[1] + FGM[2]) / 2)$chd_fgm
f$chd_tpm <- ddply(f, .(GAME_ID), transform, chd_tpm = (TPM[1] + TPM[2]) / 2)$chd_tpm
f$chd_ftm <- ddply(f, .(GAME_ID), transform, chd_ftm = (FTM[1] + FTM[2]) / 2)$chd_ftm
f$chd_to <- ddply(f, .(GAME_ID), transform, chd_to = (TO[1] + TO[2]) / 2)$chd_to
f$chd_oreb <- ddply(f, .(GAME_ID), transform, chd_oreb = (OREB[1] + OREB[2]) / 2)$chd_oreb

colnames(ncaafinal)[1] <- "GAME_ID"
ncaafinal$key <- paste(ncaafinal$GAME_ID, ncaafinal$team)
f$key <- paste(f$GAME_ID, f$TEAM.x)
all <- merge(ncaafinal, f, by="key")
all <- all[,c(2,15, 17:82)]
all<-ddply(all, .(GAME_ID.x), transform, won=pts > min(pts))
all$team <- ""
all[seq(from=1, to=dim(all)[1], by=2),]$team <- "TEAM1"
all[seq(from=2, to=dim(all)[1], by=2),]$team <- "TEAM2"
all <- all[,c(1,2,30,32,33,50,53,55:70)]
wide <- reshape(all, direction = "wide", idvar="GAME_ID.x", timevar="team")
wide$winningTeam <- "TEAM1"
wide[which(wide$won.TEAM2 == TRUE),]$winningTeam <- "TEAM2"
wide$finalScore<-(wide$pts.TEAM1 - wide$HALF_PTS.TEAM1) + (wide$pts.TEAM2 - wide$HALF_PTS.TEAM2)
#wide$finalDiff<-(wide$pts.TEAM1 - wide$HALF_PTS.TEAM1) - (wide$pts.TEAM2 - wide$HALF_PTS.TEAM2)
wide <- wide[,c(3,6:21,24,31:36,45)]


#m <- lm(finalScore ~ ., data=wide)
#m <- lm(formula = finalScore ~ HALF_PTS.TEAM1 *  LINE.TEAM1 * 
#    mwt.TEAM1 * fg_percent.TEAM1 + TPM.TEAM1 + FTM.TEAM1 + OREB.TEAM1 +
#    chd_fg.TEAM1 + LINE_HALF.TEAM1 + chd_oreb.TEAM1, data = wide)
m <- lm(formula = finalScore ~ HALF_PTS.TEAM1 + LINE.TEAM1 + mwt.TEAM1 +
    fg_percent.TEAM1 + TPM.TEAM1 + FTM.TEAM1 + OREB.TEAM1 + chd_fg.TEAM1 +
    LINE_HALF.TEAM1 + chd_oreb.TEAM1 + HALF_PTS.TEAM1:fg_percent.TEAM1,
    data = wide)

#g<-glm(as.factor(winningTeam) ~ ., family="binomial", data=wide)

## cross validate the model
accuracy <- c()
preds <- list()
actuals <- list()
for(i in 1:20){
   set.seed(i)
   test <- wide[sample(dim(wide)[1])[1:10],]
   set.seed(i)
   train <- wide[-sample(dim(wide)[1])[1:10],]
   p<-predict(m, newdata=test[,-25], interval="predict")
   #t1 <- table(data.frame(cbind(p$fit > .5, test$winningTeam)))[1,1] 
   #t2 <- table(data.frame(cbind(p$fit > .5, test$winningTeam)))[2,2]
   accuracy[i] <- cor(p[,1], test$finalScore)
   preds[[i]] <- p[,1]
   actuals[[i]] <- test$finalScore
}


save(m, file="nightlyModel.Rdat")
