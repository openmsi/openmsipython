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

LASER_SHOCK_CONST = LaserShockConstants()