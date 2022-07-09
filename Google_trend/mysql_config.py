import os
import json

from sqlalchemy import create_engine

ROOT_DIR = os.path.abspath(__file__ + '/../../')
SECRETS_PATH = 'secrets.json'
SECRETS = json.loads(open(SECRETS_PATH).read())

_DT_USER = SECRETS["DT_MYSQL_USER"]
_DT_ADDRESS = SECRETS["DT_MYSQL_ADDRESS"]
_DT_PORT = SECRETS["DT_MYSQL_PORT"]
_DT_DB = SECRETS["DT_MYSQL_DB"]
_DT_PASSWORD = SECRETS["DT_MYSQL_PASSWORD"]
_DT_URL = f'mysql+pymysql://{_DT_USER}:{_DT_PASSWORD}@{_DT_ADDRESS}:{_DT_PORT}/{_DT_DB}'


_local_user = SECRETS["MY_USER"]
_local_address = SECRETS["MY_ADDRESS"]
_local_port = SECRETS["MY_PORT"]
_local_pw = SECRETS["MY_PW"]
_local_db = SECRETS["MY_DB"]
_local_url = f'mysql+pymysql://{_local_user}:{_local_pw}@{_local_address}:{_local_port}/{_local_db}'

DT_ENGINE = create_engine(_DT_URL, echo=False, pool_recycle=3600)
MY_SQL = create_engine(_local_url, echo=False, pool_recycle=3600)