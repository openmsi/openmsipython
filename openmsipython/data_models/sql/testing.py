#imports
import os
from sqlalchemy import create_engine

#constants
UNAME = 'openmsi_writer'
PWD = os.path.expandvars('$OPENMSI_WRITER_PWORD')
HOST = 'dsp056'
DB_NAME = 'OpenMSI'

#create the engine
connection_string=f'mssql+pymssql://{UNAME}:{PWD}@{HOST}/{DB_NAME}'
engine = create_engine(connection_string,echo=True)

print(f'CONNECTION STRING = {connection_string}')
con = engine.connect()

##print out the schemas in the database
#sql = """
#SELECT s.name AS schema_name, 
#       s.schema_id,
#       u.name AS schema_owner
#FROM sys.schemas s
#    INNER JOIN sys.sysusers u
#        ON u.uid = s.principal_id
#ORDER BY s.name
#"""
#with engine.connect() as con:
#    r = con.execute(sql)
#print(f'result = {r}')
