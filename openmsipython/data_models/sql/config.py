#imports
import os

class SQLDBConstants :
    """
    Constants for the OpenMSI SQLDB
    """
    @property
    def SQL_UNAME(self) :
        return 'openmsi_writer' #Username for the SQL account
    @property
    def SQL_PWD(self) :
        return os.path.expandvars('$OPENMSI_WRITER_PWORD') #Password for the SQL account (Env var)
    @property
    def SQL_HOST(self) :
        return 'dsp056' #Host where the DB is stored
    @property
    def SQL_DB_NAME(self) :
        return 'OpenMSI' #Name of the DB on the host

SQL_CONST = SQLDBConstants()