#imports
from .utilities import get_engine

#create the engine
engine = get_engine()

#print out the schemas in the database
sql = """
SELECT s.name AS schema_name, 
       s.schema_id,
       u.name AS schema_owner
FROM sys.schemas s
    INNER JOIN sys.sysusers u
        ON u.uid = s.principal_id
ORDER BY s.name
"""
with engine.connect() as con:
    rs = con.execute(sql)
    for r in rs :
        print(r)
