import pymssql
import sqlalchemy as sqla
import getpass
import glob
import json
import os
import pandas

class MSSQLDatabase():
    # wraps a Microsoft SQL Server database
    def __init__(self,AUTH,DATABASE=None):
        # AUTH should be a dict with some specific fields useful for a direct connection to the database
        self.AUTH=AUTH
        self.SERVER=AUTH['host']
        if DATABASE is None:
            self.DATABASE=AUTH['database']
        else:
            self.DATABASE=DATABASE
        self.ENGINE=self.__create_engine()

    def execPyMSSQL(self,statement):
        with pymssql.connect(self.SERVER, self.AUTH['user'], self.AUTH['pwd'], self.DATABASE) as conn:    
            cursor = conn.cursor()
            r=cursor.execute(statement)
            conn.commit()    
        return r

    def execute_query(self,sql):
        with self.ENGINE.connect() as conn:
            return pandas.read_sql(sql,conn)
            
    def execute_update(self,statement):
        with self.ENGINE.connect() as conn:
#         r=self.ENGINE.execute(statement)
            trans = conn.begin()
            try:
                result = conn.execute(statement)
                trans.commit()
            except:
                trans.rollback()
                raise
        return result

    def __create_engine(self):
        return sqla.create_engine(f"mssql+pymssql://{self.AUTH['user']}:{self.AUTH['pwd']}@{self.SERVER}:1433/{self.DATABASE}?charset=utf8")
        
    def create_schema(self,schema):
        self.ENGINE.execute(sqla.schema.CreateSchema(schema))

    def get_source_id(self, ORG, schema='dbo'):
        sql=f"select source_id from {schema}.metadata_source where source_type='org' and organization_name='{ORG}'"
        with self.ENGINE.connect() as con:
            SOURCE_ID=pandas.read_sql(sql,con).source_id[0]
        return SOURCE_ID
        
    def drop_all_tables(self,schema,keep_tables=[]):
        tables=reversed(list(self.sorted_tables(schema).keys()))
        drop_all = "\n".join([f'drop table {schema}.{t}' for t in tables if t not in keep_tables])
        print(drop_all)
#         execPyMSSQL(drop_all)

    def delete_from_all_tables(self,schema,keep_tables=[]):
        tables=reversed(list(self.sorted_tables(schema).keys()))
        delete_all = "\n".join([f'delete from {schema}.{t}' for t in tables if t not in keep_tables])
        print(delete_all)
        execPyMSSQL(delete_all)
        
    def sorted_tables(self,schema):
        # sort tables in a schema according to FK relationship
        # returns tables ordered such tha if table t1 refers to table t2, t2 will be earlier in the result than t1
        # the 'engine' variable should be result of a SQLAlchemy create_engine statement
        with self.ENGINE.connect() as conn:
            sql=f"""
              SELECT c.table_name, string_agg(c.column_name,',') within group(order by c.ordinal_position) as columns
              ,      sum(case when c.column_name='source_id' then 1 else 0 end) as has_source_id
              ,      max(case when COLUMNPROPERTY(object_id(c.TABLE_SCHEMA+'.'+c.TABLE_NAME), c.COLUMN_NAME, 'IsIdentity') = 1 then c.column_name else null end) as identity_column
              from information_Schema.tables t
              join information_schema.columns c on c.table_schema=t.table_schema and c.table_name=t.table_name
             where t.table_schema = '{schema}' and t.table_type='BASE TABLE'
             group by c.table_name
            """
            tables=pandas.read_sql(sql,conn)
            tables={t.table_name:{'columns':t.columns,'identity_column':t.identity_column,'has_source_id':t.has_source_id,'FKs':set()} for t in tables.itertuples()}

            sql=f"""
            SELECT OBJECT_NAME(fk.parent_object_id) as from_table
            ,      OBJECT_NAME(fk.referenced_object_id) to_table
              FROM sys.foreign_keys fk
              INNER JOIN sys.foreign_key_columns fkc 
                 ON fkc.constraint_object_id = fk.object_id
              INNER JOIN sys.columns c1 
                 ON fkc.parent_column_id = c1.column_id 
                AND fkc.parent_object_id = c1.object_id
              INNER JOIN sys.columns c2 
                 ON fkc.referenced_column_id = c2.column_id 
                AND fkc.referenced_object_id = c2.object_id
              inner join sys.schemas s on s.schema_id=fk.schema_id
          where s.name='{schema}'
            """
            FKs=pandas.read_sql(sql,conn)
            for f in FKs.itertuples():
                tables[f.from_table]['FKs'].add(f.to_table)

        ordered=[]
        done=set()
        def topsort(t):
            if t not in tables:
                return
            refs=tables[t]['FKs']
            for r in refs:
                if r in done:
                    continue
                topsort(r)
            ordered.append(t)
            done.add(t)

        for t in tables:
            if t not in done:
                topsort(t)
        return {t:{'columns':tables[t]['columns'],
                   'identity_column':tables[t]['identity_column'],
                   'has_source_id':True if tables[t]['has_source_id']==1 else False,'FKs':tables[t]['FKs'] if len(tables[t]['FKs'])>0 else None} for t in ordered}