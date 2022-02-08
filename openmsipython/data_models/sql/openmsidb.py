#imports
from contextlib import contextmanager
from sqlalchemy import text
from ...shared.logging import LogOwner
from .utilities import get_engine

class OpenMSIDB(LogOwner) :
    """
    Class for working with the OpenMSI SQL database using sqlalchemy methods
    """

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        self.engine=get_engine()

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
