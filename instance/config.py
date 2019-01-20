import os
class OverallConfig(object):
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    DATABASE = 'workplan'
    POSTGRES = {
    'user':'keronei',
    'pw':'',
    'db':'workplan',
    'host':'localhost',
    'port':'5432'
     }
    SQLALCHEMY_DATABASE_URI =  'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s'%POSTGRES
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    
class Development(OverallConfig):
    """
    dev environ configuration
    """
    DEBUG = True
    TESTING = True
    

class Testing():
    DATABASE = 'tests'
    POSTGREST = {
    'user':'keronei',
    'pw':'',
    'db':'tests',
    'host':'localhost',
    'port':'5432'
     }
    SQLALCHEMY_DATABASE_URI =  'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s'%POSTGREST
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    TESTING = True
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    
    
class Production(OverallConfig):
    """
    pro env config
    """
    DEBUG = False
    TESTING = False    
    
app_config = {
    'development': Development,
    'production': Production,
    'testing':Testing,
}
        
