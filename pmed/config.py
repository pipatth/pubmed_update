import os

# database config
class Config(object):
    '''common config'''
    DB_CONFIG = {
        'endpoints': os.environ.get('PUBMED_ENDPOINTS', None),
        'dbname': os.environ.get('PUBMED_DBNAME', None),
        'username': os.environ.get('PUBMED_USERNAME', None),
        'password': os.environ.get('PUBMED_PASS', None),
        'pool_recycle': 3600
    }
    for k,v in DB_CONFIG.items():
        if v is None:
            raise ValueError('Environment variable is missing for ' + k)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_CONFIG['username'] + ':' + DB_CONFIG['password'] + '@' + DB_CONFIG['endpoints'] + '/' + DB_CONFIG['dbname'] + '?charset=utf8mb4'
