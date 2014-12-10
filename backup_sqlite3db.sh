NOW=$(date +"%m-%d-%Y-%H%M%S")
/usr/bin/s3cmd --config /home/ec2-user/.s3cfg --no-progress -v put sports.db s3://sqlitebackups/$NOW-sports.db

