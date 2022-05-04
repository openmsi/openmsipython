#imports
import pathlib, methodtools
from threading import Lock
from dataclasses import fields, is_dataclass
from atomicwrites import atomic_write
from .logging import LogOwner

class DataclassTable(LogOwner) :
    """
    A class to work with an atomic csv file that's holding dataclass entries in a thread-safe way
    """

    @methodtools.lru_cache()
    @property
    def csv_header_line(self) :
        s = ''
        for fieldname in self.__field_names :
            s+=f'{fieldname},'
        return s[:-1]

    def __init__(self,dataclass_type,*args,filepath=None,key_attr_name=None,**kwargs) :
        """
        dataclass_type = the dataclass that entries in this file will represent
        filepath = the path to the csv file that should be created/read from
                   (default is a file named after the dataclass type in the current directory)
        key_attr_name = the name of the dataclass attribute that can be used to key the dictionary of objects
                        assumed to be unique among all objects
                        keying the objects in a dictionary makes it faster to update
        """
        #init the LogOwner
        super().__init__(*args,**kwargs)
        #figure out what type of objects the table/file will be describing
        self.__dataclass_type = dataclass_type
        if not is_dataclass(self.__dataclass_type) :
            self.logger.error(f'ERROR: "{self.__dataclass_type}" is not a dataclass!',TypeError)
        if len(fields(self.__dataclass_type)) <= 0 :
            errmsg = f'ERROR: dataclass type {self.__dataclass_type} does not have any fields '
            errmsg+= f'and so cannot be used in a {self.__class__.__name__}!'
            self.logger.error(errmsg,ValueError)
        self.__field_names = [field.name for field in fields(self.__dataclass_type)]
        self.__field_types = [field.type for field in fields(self.__dataclass_type)]
        #figure out where the csv file should go
        self.__filepath = filepath if filepath is not None else pathlib.Path() / f'{self.__dataclass_type.__name__}.csv'
        #figure out how to key the dictionaries of entry objects and entry lines
        self.__key_attr_name = key_attr_name 
        #set some other variables
        self.__lock = Lock()
        self.__entry_objs = {} if self.__key_attr_name is not None else []
        self.__entry_lines = {} if self.__key_attr_name is not None else []
        #read or create the file to finish setting up the table
        if self.__filepath.is_file() :
            self.__read_csv_file()
        else :
            msg = f'Creating new {self.__class__.__name__} csv file at {self.__filepath} '
            msg+= f'to hold {self.__dataclass_type.__name__} entries'
            self.logger.info(msg)
            self.__write_lines(self.csv_header_line)

    def __read_csv_file(self) :
        """
        Read in a csv file with lines of the expected dataclass type
        """
        msg = f'Reading {self.__class__.__name__} csv file at {self.__filepath} '
        msg+= f'to get {self.__dataclass_type} entries...'
        self.logger.info(msg)
        #read the file
        with open(self.__filepath,'r') as fp :
            lines_as_read = fp.readlines()
        #first make sure the header line matches what we'd expect for the dataclass
        if lines_as_read[0].strip()!=self.csv_header_line :
            errmsg = f'ERROR: header line in {self.__filepath} ({lines_as_read[0]}) does not match expectation for '
            errmsg+= f'{self.__dataclass_type} ({self.csv_header_line})!'
            self.logger.error(errmsg)
        #add entry lines and objects
        for line in lines_as_read[1:] :
            obj = self.__obj_from_line(line)
            if self.__key_attr_name is None :
                self.__entry_objs.append(obj)
                self.__entry_lines.append(line)
            else :
                dkey = getattr(obj,self.__key_attr_name)
                if (dkey in self.__entry_objs.keys()) or (dkey in self.__entry_lines.keys()) :
                    errmsg = f'ERROR: found duplicate entry for key "{dkey}" from {self.__key_attr_name} '
                    errmsg+= f'in {self.__filepath}!'
                    self.logger.error(errmsg,RuntimeError)
                self.__entry_objs[dkey] = obj
                self.__entry_lines[dkey] = line
        self.logger.info(f'Found {len(self.__entry_objs)} {self.__dataclass_type.__name__} entries in {self.__filepath}')

    def __write_lines(self,lines,overwrite=True) :
        """
        Write a line or container of lines to the csv file, in a thread-safe and atomic way
        """
        if type(lines)==str :
            lines = [lines]
        lines_string = ''
        for line in lines :
            lines_string+=f'{line.strip()}\n'
        try :
            with self.__lock :
                with atomic_write(self.__filepath,overwrite=overwrite) as fp :
                    fp.write(lines_string)
        except Exception as e :
            errmsg = f'ERROR: failed to write to {self.__class__.__name__} csv file at {self.__filepath}! '
            errmsg+=  'Will reraise exception.'
            self.logger.error(errmsg,exc_obj=e)

    def __line_from_obj(self,obj) :
        """
        Return the csv file line for a given object
        """
        if obj.__class__ != self.__dataclass_type :
            self.logger.error(f'ERROR: "{obj}" is mismatched to type {self.__dataclass_type}!',TypeError)
        s = ''
        for fname in self.__field_names :
            s+=f'{str(getattr(obj,fname))},'
        return s[:-1]

    def __obj_from_line(self,line) :
        """
        Return the dataclass instance for a given csv file line string
        """
        args = []
        for attrtype,attrstr in zip(self.__field_types,(line.strip().split(','))) :
            args.append(attrtype(attrstr))
            return self.__dataclass_type(*args)
