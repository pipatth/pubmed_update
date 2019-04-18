# database config
class Config(object):
    '''common config'''
    DB_CONFIG = {
        'endpoints': '127.0.0.1',
        'dbname': 'rvcapdb',
        'username': 'rvcap',
        'password': 'rWJ5is53',
        'pool_recycle': 3600
    }
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_CONFIG['username'] + ':' + DB_CONFIG['password'] + '@' + DB_CONFIG['endpoints'] + '/' + DB_CONFIG['dbname'] + '?charset=utf8mb4'
