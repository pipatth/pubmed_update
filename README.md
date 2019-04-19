# Harvard Capstone Reference Visualization PubMed SQL Database Update

### Collaborators: Arthur, Mohammad, David, Pipat

#### How to setup 
- Using a Ubuntu 18.04 VM or container with Python 3.7.2
- Create a blank MySQL database with Unicode-8 character set
```
mysql> CREATE DATABASE <your_database_name> CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
- Modify config.py to your MySQL database
- Install VirtualEnv if you don't have it:
```
$ pip install virtualenv
```
- Create virtual environment 
```
$ virtualenv env
$ source env/bin/activate
```
- Install pubmed-parser from git
```
$ git clone https://github.com/pipatth/pubmed_parser
$ pip install ./pubmed_parser
```
- Install other dependencies
```
$ pip install -r requirements.txt
```
- Change 'PUBMED_UPDATE_PATH' and 'PUBMED_VENV_PATH' your full path. For example, if the code is in ~/pubmed_update and the virtualenv is in ~/pubmed_update/env/bin/activate, then change to:
```
export PUBMED_UPDATE_PATH=~/pubmed_update/env/bin/activate
export PUBMED_VENV_PATH=~/pubmed_update
```
- Start a Luigi server
```
$ luigid 
```

#### To run a one-time update on database:
- cd into the directory 'pubmed_update'
- Run bash script run.sh
```
$ ./run.sh
```

#### To schedule a cron job to run update nightly:
- Open crontab
```
$ crontab -e
```
- Add the following line to the file (change time and run.sh location  as you wish)
```
<minute> <hour> * * * <path_to_run.sh> > /tmp/listener.log 2>&1
```
#### To view the running task on Luigi:
- Open a browser to http://127.0.0.1:8082