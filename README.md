# Harvard Capstone Reference Visualization PubMed SQL Database Update

### Collaborators: Arthur, Mohammad, David, Pipat

#### Requirements:
- Ubuntu 18.04 
- Python 3.7.2
- MySQL 5.7

#### Set up a local MySQL database (skip this if cloud provider)
- Login to MySQL
```
$ mysql -u <your_mysql_username> -p
```
Create a blank MySQL database with Unicode-8 character set
```
mysql> CREATE DATABASE <your_database_name> CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Set up a Luigi
- Install VirtualEnv if you don't have it:
```
$ pip install virtualenv
```
- Clone this repository and create virtual environment 
```
$ git clone https://github.com/pipatth/pubmed_update
$ cd pubmed_update
$ virtualenv env
```
- Activate the virtual environment
```
$ source env/bin/activate
```
- Install pubmed-parser from git
```
$ cd ..
$ git clone https://github.com/pipatth/pubmed_parser
$ pip install ./pubmed_parser
```
- Install other dependencies
```
$ cd pubmed_update
$ pip install -r requirements.txt
```
- Start a Luigi server
```
$ luigid 
```
- To view the running task on Luigi, open a browser to http://127.0.0.1:8082

#### To run a one-time update on database:
- cd into the directory 'pubmed_update'
- In run_sample.sh Change 'PUBMED_UPDATE_PATH' and 'PUBMED_VENV_PATH' to your full path. For example, if the code is in ~/pubmed_update and the virtualenv is in ~/pubmed_update/env/bin/activate, then change to:
```
export PUBMED_UPDATE_PATH=~/pubmed_update/env/bin/activate
export PUBMED_VENV_PATH=~/pubmed_update
```
- Set environment variables
```
$ export PUBMED_ENDPOINTS=<your_mysql_ip_host>
$ export PUBMED_DBNAME=<your_database_name>
$ export PUBMED_USERNAME=<your_mysql_username>
$ export PUBMED_PASS=<your_mysql_password>
```
- Run bash script run_sample.sh
```
$ ./run_sample.sh
```

#### To run a one-time update on database:
- cd into the directory 'pubmed_update'
- In run.sh Change 'PUBMED_UPDATE_PATH' and 'PUBMED_VENV_PATH' to your full path. For example, if the code is in ~/pubmed_update and the virtualenv is in ~/pubmed_update/env/bin/activate, then change to:
```
export PUBMED_UPDATE_PATH=~/pubmed_update/env/bin/activate
export PUBMED_VENV_PATH=~/pubmed_update
```
- Set environment variables
```
$ export PUBMED_ENDPOINTS=<your_mysql_ip_host>
$ export PUBMED_DBNAME=<your_database_name>
$ export PUBMED_USERNAME=<your_mysql_username>
$ export PUBMED_PASS=<your_mysql_password>
```
- Run bash script run.sh
```
$ ./run.sh
```

#### To schedule a cron job to run update nightly:
- Open crontab
```
$ crontab -e
```
- Add environment variables at the top of run.sh
```
export PUBMED_ENDPOINTS=<your_mysql_ip_host>
export PUBMED_DBNAME=<your_database_name>
export PUBMED_USERNAME=<your_mysql_username>
export PUBMED_PASS=<your_mysql_password>
```
- Add the following line to the file (change time and run.sh location  as you wish)
```
<minute> <hour> * * * <path_to_run.sh> > /tmp/listener.log 2>&1
```
