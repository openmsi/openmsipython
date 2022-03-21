#imports
from .openmsidb import OpenMSIDB

def main() :
    #create the DB
    openmsi_db = OpenMSIDB()
    #print out the schemas in the database
    print('Schemas:')
    sql = """
    SELECT s.name AS schema_name, 
        s.schema_id,
        u.name AS schema_owner
    FROM sys.schemas s
        INNER JOIN sys.sysusers u
            ON u.uid = s.principal_id
    ORDER BY s.name
    """
    with openmsi_db.query_result(sql) as res :
        for row in res :
            print(row)
    table_names = [
        'glassIDs',
        'epoxyIDs',
        'foilIDs',
        'spacerIDs',
        'flyercuttingprograms',
        'spacercuttingprograms',
        'flyerstacks',
        'samples',
        'launchpackages',
        'experiments',
    ]
    #print out the entries in the database
    for table_name in table_names :
        print(f'Entries in laser_shock_gemd.{table_name}:')
        sql = f"SELECT * FROM laser_shock_gemd.{table_name}"
        with openmsi_db.query_result(sql) as res :
            for row in res :
                print(row)
        print('')
    print('Done.')

if __name__=='__main__' :
    main()
