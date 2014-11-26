## amzn-ami-hvm-2014.09.1.x86_64-ebs (ami-b66ed3de)
sudo yum -y update
sudo yum -y install git
sudo yum -y install gcc
sudo yum -y install gcc-c++
sudo yum -y install libxslt-devel
sudo yum -y install libxml2-devel
sudo yum -y install gpgme-devel
sudo yum -y install Cython
sudo yum -y install python-devel

sudo easy_install BeautifulSoup4
sudo easy_install pip
sudo pip install pandas
sudo easy_install flask
sudo easy_install fast
sudo easy_install lxml

git clone https://github.com/tcash21/sports.git
cd sports
sqlite3 sports.db < sports.sql 

