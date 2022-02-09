#imports
from ...shared.runnable import Runnable
from ..sql.openmsidb import OpenMSIDB

class LaserShockSQLDB(OpenMSIDB,Runnable) :
    """
    Class to handle the laser shock portion of the OpenMSI SQL database
    """

    SCHEMA = 'laser_shock_gemd' #Name of the schema in the SQL DB that stores the Laser Shock Lab's GEMD data model

    def recreate_from_files(self,json_dir) :
        """
        Recreate the SQL DB with JSON entries for every object dumped to a directory of files

        json_dir = path to the directory holding all of the JSON files that should be added to the database
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
        #insert new records
        for glassIDfp in json_dir.glob('LaserShockGlassID_*.json') :
            json_content = None
            with open(glassIDfp,'r') as fp :
                json_content = fp.read()
            sql = f"""
            INSERT INTO {self.SCHEMA}.glassIDs (obj) VALUES ({json_content})
            """
            self.execute(sql)

    @classmethod
    def get_command_line_arguments(cls) :
        args = ['gemd_json_dir']
        kwargs = {}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        db = cls()
        #recreate the SQL database from dumped JSON files
        db.recreate_from_files(args.gemd_json_dir)    

#################### MAIN FUNCTION ####################

def main(args=None) :
    LaserShockSQLDB.run_from_command_line(args)

if __name__=='__main__' :
    main()