# Harvard Capstone Reference Visualization PubMed SQL Database Update

### Collaborators: Arthur, Mohammad, David, Pipat

#### How to setup 
- Modify config.py to your MySQL database
- Install VirtualEnv if you dont have it:
```
pip install virtualenv
```
- Create virtual environment and install dependencies
```
virtualenv env
source env/bin/activate (This doesn't work on windows - For windows use "env\Scripts\activate". Note: you'll need admin permissions to run this script -- Open powershell in Admin mode and enter "Set-ExecutionPolicy Unrestricted" and hit "Y")
pip install -r requirements.txt
```
- Start a Luigi server
```
luigid
```
- To run update on database
```
python pmed/pipeline.py UpdateCiteCountTask --LoadDataTask-include-nodata 0
```
