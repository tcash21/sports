library(randomForest)
library(dplyr)
library(plyr)
library(RSQLite)

drv <- dbDriver("SQLite")
con <- dbConnect(drv, "/home/ec2-user/sports/sports.db")

tables <- dbListTables(con)

lDataFrames <- vector("list", length=length(tables))


 ## create a data.frame for each table
for (i in seq(along=tables)) {
  if(tables[[i]] == 'NCAASBHalfLines' | tables[[i]] == 'NCAASBLines'){
  # lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste0("SELECT n.away_team, n.home_team, n.game_date, n.line, n.spread, n.game_time from '", tables[[i]], "' n inner join
  #(select game_date, away_team,home_team, max(game_time) as mgt from '", tables[[i]], "' group by game_date, away_team, home_team) s2 on s2.game_date = n.game_date and
  #s2.away_team = n.away_team and s2.home_team = n.home_team and n.game_time = s2.mgt and n.game_date = '", format(as.Date(input$date),"%m/%d/%Y"),  "';"))
   lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste0("SELECT * FROM ", tables[[i]], " where game_date = '", format(as.Date(input$date), "%m/%d/%Y"), "';"))

  } else if (tables[[i]] == 'NCAAseasontotals' | tables[[i]] == 'NCAAseasonstats') {
         lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[i]], "' where the_date = '", format(as.Date(input$date), "%m/%d/%Y"), "'", sep=""))
  } else if (tables[[i]] %in% c('NCAAgames')) {
         lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[i]], "' where game_date = '", format(as.Date(input$date), "%m/%d/%Y"), "'", sep=""))
  } else {
        lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[i]], "'", sep=""))
  }
  cat(tables[[i]], ":", i, "\n")
}

lines <- lDataFrames[[3]]
final <- lDataFrames[[5]]
games <- lDataFrames[[6]]
lookup <- lDataFrames[[4]]
lines <- subset(lines, line != "0")

games$away_team<-lookup[match(games$team1, lookup$espn_abbr),]$sb_team
games$home_team<-lookup[match(games$team2, lookup$espn_abbr),]$sb_team
games$key<-paste(games$game_date, games$away_team, games$home_team)

lines$key<-paste(lines$game_date, lines$away_team, lines$home_team)
lines$game_time<-as.POSIXlt(lines$game_time)
lines<-lines[order(lines$home_team, lines$game_time),]
lines$game_time<-as.character(lines$game_time)

changes<-ddply(lines, .(key), summarize, numChanges=length(key))
fl<-ddply(lines, .(away_team, home_team, game_date), function(x) x[c(1, nrow(x)),])
fl$line <- as.numeric(fl$line)
##fl <- fl[-grep(' 00:', fl$game_time),]
fl$key <- paste(fl$game_date, fl$away_team, fl$home_team)

fl$line_change<- rep(aggregate(line ~ key, data=fl, function(x) x[2] - x[1])[,2], each=2)
fl<-fl[seq(2, dim(fl)[1], by=2),]
fl$numChanges<-changes[match(fl$key, changes$key),]$numChanges

l<-lines[match(games$key, lines$key,0),]
games<-games[match(l$key, games$key),]
fl <- fl[match(games$key, fl$key),]
all<-cbind(fl, games)
x<-merge(all, final,by=c("game_id"))
y<-ddply(x, .(key), transform, total=sum(pts[1]+pts[2]))
y$over <- y$total > y$line

y$positive <- y$line_change > 0
y[which(y$positive == TRUE),]$positive <- "POSITIVE"
y[which(y$positive == FALSE),]$positive <- "NEGATIVE"

