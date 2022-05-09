#imports
import pathlib, methodtools, datetime, typing
from threading import Lock
from dataclasses import fields, is_dataclass
from atomicwrites import atomic_write
from .logging import LogOwner

class DataclassTable(LogOwner) :
    """
    A class to work with an atomic csv file that's holding dataclass entries in a thread-safe way
    """

    #################### PROPERTIES AND CONSTANTS ####################

    DELIMETER = ';' #can't use a comma or containers would display incorrectly
    DATETIME_FORMAT = '%m/%d/%Y at %H:%M:%S'

    @methodtools.lru_cache
    @property
    def NESTED_TYPES(self) :
        simple_types = [str,int,float,complex,bool]
        container_types = [(typing.List,list),(typing.Tuple,tuple),(typing.Set,set)]
        rd = {}
        for c_t in container_types :
            for s_t in simple_types :
                rd[c_t[s_t]] = (c_t,s_t)
        return rd

    @methodtools.lru_cache()
    @property
    def csv_header_line(self) :
        s = ''
        for fieldname in self.__field_names :
            s+=f'{fieldname},'
        return s[:-1]

    @property
    def obj_addresses(self) :
        return self.__entry_objs.keys()

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,dataclass_type,*args,filepath=None,**kwargs) :
        """
        dataclass_type = the dataclass that entries in this file will represent
        filepath = the path to the csv file that should be created/read from
                   (default is a file named after the dataclass type in the current directory)
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
        #set some other variables
        self.__lock = Lock()
        self.__entry_objs = {}
        self.__entry_lines = {}
        #read or create the file to finish setting up the table
        if self.__filepath.is_file() :
            self.__read_csv_file()
        else :
            msg = f'Creating new {self.__class__.__name__} csv file at {self.__filepath} '
            msg+= f'to hold {self.__dataclass_type.__name__} entries'
            self.logger.info(msg)
            self.__write_lines(self.csv_header_line)

    def add_entries(self,new_entries) :
        """
        Add a new set of entries to the table

        new_entry_obj = the new entry to add to the table
        """
        pass

    def get_entry_attrs(self,entry_obj_address,*args,**kwargs) :
        """
        Return a dictionary of all or some of the current attributes of am entry in the table
        Use args/kwargs to get either a list or a dictionary returned, 
        where args/kwargs are names of attribute values to return.

        entry_obj_address = the address in memory of the object to return attributes for
        """
        pass

    def set_entry_attrs(self,entry_obj_address,attr_names_values) :
        """
        Modify attributes of an entry that already exists in the table

        entry_obj_address = The address in memory of the entry object to modify 
        attr_names_values = A dictionary of attributes to set (keys are names, values are values for those named attrs)
        """
        pass

    @methodtools.lru_cache(maxsize=3)
    def obj_addresses_by_key_attr(self,key_attr_name) :
        """
        Return a dictionary whose keys are the values of some given attribute for each object 
        and whose values are lists of the addresses in memory of the objects in the table
        that have each value of the requested attribute
        
        Useful to find objects in the table by attribute values so they can be efficiently updated 
        without compromising the integrity of the objects in the table and their attributes
        
        Up to 3 return values are cached so you can work with more than one view of the objects in the table at a time

        key_attr_name = the name of the attribute whose values should be used as keys in the returned dictionary
        """
        pass

    #################### PRIVATE HELPER FUNCTIONS ####################

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
            #key both dictionaries by the address of the object in memory
            dkey = hex(id(obj))
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
        for fname,ftype in zip(self.__field_names,self.__field_types) :
            s+=f'{self.__get_str_from_attribute(getattr(obj,fname),ftype)}{self.DELIMETER}'
        return s[:-1]

    def __obj_from_line(self,line) :
        """
        Return the dataclass instance for a given csv file line string
        """
        args = []
        for attrtype,attrstr in zip(self.__field_types,(line.strip().split(','))) :
            args.append(self.__get_attribute_from_str(attrstr,attrtype))
            return self.__dataclass_type(*args)

    def __get_str_from_attribute(self,attrobj,attrtype) :
        """
        Given an object and the type it is in the dataclass, 
        return the string representation of it that should go in the file
        """
        if attrtype==datetime.datetime :
            return repr(attrobj.strftime(self.DATETIME_FORMAT))
        else :
            return repr(attrobj)

    def __get_attribute_from_str(self,attrstr,attrtype) :
        """
        Given the string of the repr() output of some object and the datatype it represents, return the actual object
        """
        #datetime objects are handled in a custom way
        if attrtype==datetime.datetime :
            return datetime.datetime.strptime(attrstr[1:-1],self.DATETIME_FORMAT)
        #strings have extra quotes on either end
        elif attrtype==str :
            return attrtype(attrstr[1:-1])
        #int, float, complex, and bool can all be directly re-casted
        elif attrtype in (int,float,complex,bool) :
            return attrtype(attrstr)
        #some simply-nested container types can be casted in two steps
        elif attrtype in self.NESTED_TYPES.keys() :
            to_cast = []
            for vstr in attrstr[1:-1].split(',') :
                to_cast.append(self.NESTED_TYPES[attrtype][1](vstr))
            return self.NESTED_TYPES[attrtype][0](to_cast)
        else :
            errmsg = f'ERROR: attribute type "{attrtype}" is not recognized for a {self.__class__.__name__}!'
            self.logger.error(errmsg,ValueError)
