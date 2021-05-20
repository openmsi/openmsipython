#imports
from ..utilities.logging import Logger
import pathlib, configparser

class ConfigFileParser :
    """
    A class to parse configurations from files
    """

    #################### PROPERTIES ####################

    @property
    def available_group_names(self):
        return self._config.sections()

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,config_path,**kwargs) :
        """
        config_path = path to the config file to parse

        Possible keyword arguments:
        logger = the logger object to use
        """
        self._filepath = config_path
        self._logger = kwargs.get('logger')
        if self._logger is None :
            self._logger = Logger(pathlib.Path(__file__).name.split('.')[0])
        if not config_path.is_file() :
            self._logger.error(f'ERROR: configuration file {config_path} does not exist!',FileNotFoundError)
        self._config = configparser.ConfigParser()
        self._config.read(config_path)
    
    def get_config_dict_for_groups(self,group_names) :
        """
        Return a config dictionary populated with configurations from groups with the given names

        group_names = the list of group names to add to the dictionary
        """
        if isinstance(group_names,str) :
            group_names = [group_names]
        config_dict = {}
        for group_name in group_names :
            if group_name not in self._config :
                self._logger.error(f'ERROR: {group_name} is not a recognized section in {self._filepath}!',ValueError)
            for key, value in self._config[group_name].items() :
                config_dict[key] = value
        return config_dict

