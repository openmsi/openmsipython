#imports
from ..sql.openmsidb import OpenMSIDB

class LaserShockSQLDB(OpenMSIDB) :
    """
    Class to handle the laser shock portion of the OpenMSI SQL database
    """

    SCHEMA = 'laser_shock_gemd' #Name of the schema in the SQL DB that stores the Laser Shock Lab's GEMD data model

    def recreate_from_files(self) :
        """
        Recreate the SQL DB with JSON entries for every object dumped to a directory of files
        """
        self.logger.info('Recreating the SQL DB...')
        #create the schema if it doesn't already exist
        schema_exists = False
        with self.query_result("SELECT s.name AS schema_name FROM sys.schemas s") as res :
            for row in res :
                if row['schema_name']==self.SCHEMA :
                    schema_exists = True
                    break
        if not schema_exists :
            self.execute(f"CREATE SCHEMA {self.SCHEMA}")
        #drop existing tables that we're going to replace
        self.execute(f'DROP TABLE IF EXISTS {self.SCHEMA}.glassIDs')
        #set up the new tables
        sql = f"""
        CREATE TABLE {self.SCHEMA}.glassIDs (
            id BIGINT PRIMARY KEY IDENTITY,
            obj NVARCHAR(8000)
        )
        """
        self.execute(sql)
        ##insert new records
        #encoder = GEMDJson()
        #for glassid in self.glass_IDs :
        #    json_to_insert = encoder.thin_dumps(glassid.spec,indent=2)
        #    sql = f"""
        #    INSERT INTO {self.SCHEMA}.glassIDs (obj) VALUES ({json_to_insert})
        #    """
        #    self.execute(sql)

#################### MAIN FUNCTION ####################

def main() :
    db = LaserShockSQLDB()
    #recreate the SQL database from dumped JSON files
    db.recreate_from_files()

if __name__=='__main__' :
    main()