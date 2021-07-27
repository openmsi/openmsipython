#imports
import os, configparser
from ..utilities.logging import LogOwner

class ConfigFileParser(LogOwner) :
    """
    A class to parse configurations from files
    """

    #################### PROPERTIES ####################

    @property
    def available_group_names(self):
        return self._config.sections()

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,config_path,*args,**kwargs) :
        """
        config_path = path to the config file to parse
        """
        super().__init__(*args,**kwargs)
        self._filepath = config_path
        if not config_path.is_file() :
            self.logger.error(f'ERROR: configuration file {config_path} does not exist!',FileNotFoundError)
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
                self.logger.error(f'ERROR: {group_name} is not a recognized section in {self._filepath}!',ValueError)
            for key, value in self._config[group_name].items() :
                #if the value is an environment variable, expand it on the current system
                if value.startswith('$') :
                    exp_value = os.path.expandvars(value)
                    if exp_value == value :
                        self.logger.error(f'ERROR: Expanding {value} in {self._filepath} as an environment variable failed (must be set on system)',ValueError)
                    else :
                        value = exp_value
                config_dict[key] = value
        return config_dict

