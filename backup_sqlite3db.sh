NOW=$(date +"%m-%d-%Y-%H%M%S")
s3cmd put sports.db s3://sqlitebackups/$NOW-sports.db

