#imports
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import text
from ...shared.logging import LogOwner
from .config import SQL_CONST

class OpenMSIDB(LogOwner) :
    """
    Class for working with the OpenMSI SQL database using sqlalchemy methods
    """

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        self.engine=self.__get_engine()

    def execute(self,sql) :
        """
        Execute a plaintext SQL command without returning the result
        """
        try :
            with self.engine.connect() as con :
                _ = con.execute(text(sql))
        except Exception as e :
            self.logger.error(f'ERROR: Will reraise exception "{e}" from executing "{sql}"',exc_obj=e)
    
    @contextmanager
    def query_result(self,query) :
        """
        Return the result of a plaintext SQL query (managed in a context)
        """
        con = None
        try :
            con = self.engine.connect()
            yield con.execute(text(query))
        except Exception as e :
            self.logger.error(f'ERROR: Will reraise exception "{e}" from getting result of query "{query}"',exc_obj=e)
        finally :
            if con is not None :
                con.close()

    def __get_engine(self,uname=SQL_CONST.SQL_UNAME,pwd=SQL_CONST.SQL_PWD,
                     host=SQL_CONST.SQL_HOST,db_name=SQL_CONST.SQL_DB_NAME) :
        #create and return the engine
        connection_string=f'mssql+pymssql://{uname}:{pwd}@{host}/{db_name}'
        engine = create_engine(connection_string,echo=True)
        return engine
