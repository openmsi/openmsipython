def add_kwargs_to_configs(configs,**kwargs) :
    """
    Add any kwargs with underscores replaced with dots to a given config dictionary
    """
    new_configs = configs.copy()
    for argname,arg in kwargs.items() :
        new_configs[argname.replace('_','.')]=arg
    return new_configs
