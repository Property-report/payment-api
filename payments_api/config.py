import os

APP_NAME = os.environ['APP_NAME']
AUTHORIZE_URI= os.environ['AUTHORIZE_URI']
CLIENT_ID= os.environ['CLIENT_ID']
API_KEY=os.environ['API_KEY']
SITE=os.environ['SITE']
TOKEN_URI=os.environ['TOKEN_URI']
PUBLIC_KEY=os.environ['PUBLIC_KEY']
webhook_url=os.environ['webhook_url']

SECRET_KEY = os.environ['SECRET_KEY']
postgresql_string = 'postgresql://{}:{}@{}:{}/{}'
SQLALCHEMY_MIGRATE_REPO = os.environ['SQLALCHEMY_MIGRATE_REPO']
redirect_uri=os.environ['redirect_uri']

SQLALCHEMY_USER = os.environ['SQLALCHEMY_USER']
SQLALCHEMY_PASSWORD = os.environ['SQLALCHEMY_PASSWORD']
SQLALCHEMY_HOST = os.environ['SQLALCHEMY_HOST']
SQLALCHEMY_PORT = os.environ['SQLALCHEMY_PORT']
SQLALCHEMY_DB = os.environ['SQLALCHEMY_DB']
SQLALCHEMY_DATABASE_URI = postgresql_string.format(SQLALCHEMY_USER, SQLALCHEMY_PASSWORD, SQLALCHEMY_HOST, SQLALCHEMY_PORT, SQLALCHEMY_DB)



SET_POOL = 20
