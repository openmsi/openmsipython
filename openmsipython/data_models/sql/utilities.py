#imports
from sqlalchemy import create_engine
from .config import SQL_CONST

def get_engine() :
    #create asnd return the engine
    connection_string=f'mssql+pymssql://{SQL_CONST.SQL_UNAME}:{SQL_CONST.SQL_PWD}'
    connection_string+=f'@{SQL_CONST.SQL_HOST}/{SQL_CONST.SQL_DB_NAME}'
    print(f'connection_string = {connection_string}')
    engine = create_engine(connection_string,echo=True)
    return engine
