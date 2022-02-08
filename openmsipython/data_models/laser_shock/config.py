class LaserShockConstants :
    """
    Constants for Laser Shock Lab stuff and the associated FileMaker Database
    """
    @property
    def FILEMAKER_SERVER_IP_ADDRESS(self) :
        return 'https://10.173.38.223' #IP Address of the FileMaker DB Server within the Hopkins VPN
    @property
    def DATABASE_NAME(self) :
        return 'Laser Shock' #Name of the Laser Shock Lab's FileMaker database
    @property
    def SQL_DB_SCHEMA(self) :
        return 'laser_shock_gemd' #Name of the schema in the SQL DB that stores the Laser Shock Lab's GEMD data model

LASER_SHOCK_CONST = LaserShockConstants()