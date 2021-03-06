library(sendmailR)

## Checks to make sure each game has 2 rows, if not something may have failed with the lookup table

test <- read.csv("/home/ec2-user/sports/testfile.csv")
df <- data.frame(table(test$game_id))
if(dim(df)[1] > 0){
 if(length(which(df$Freq == 1)) == 1){
 sendmailV <- Vectorize( sendmail , vectorize.args = "to" )
 #emails <- c( "<tanyacash@gmail.com>" , "<malloyc@yahoo.com>" )
 emails <- c("<tanyacash@gmail.com>")

 from <- "<tanyacash@gmail.com>" 
 subject <- "Error Detected"
 body <- c(
  "See the attached file.",
  mime_part("/home/ec2-user/sports/testfile.csv", "WeeklyData.csv")
 )
 sendmailV(from, to=emails, subject, body)
}
}
