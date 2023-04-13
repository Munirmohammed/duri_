import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

user = os.getenv('POSTGRES_USER')
host = os.getenv('POSTGRES_SERVER')
port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')
#region = os.getenv('AWS_REGION')
#secret_name = os.getenv('DB_PASSWORD_SECRET_NAME')
password = os.getenv('POSTGRES_PASSWORD', None)

def get_db_url():
    '''
        To support db password retrival for all environment types
            - env variable
            - secret manager
            - IAM
    '''
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return DATABASE_URL

def make_engine():
    db_url = get_db_url()
    print('connecting to => ', db_url)
    return create_engine(db_url, echo=False, pool_pre_ping=True, pool_size=100, max_overflow=150)

engine = make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
