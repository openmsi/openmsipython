#imports
from openmsistream.running.argument_parsing import existing_dir, OpenMSIStreamArgumentParser

class OpenMSIPythonArgumentParser(OpenMSIStreamArgumentParser) :

    ARGUMENTS = {**OpenMSIStreamArgumentParser.ARGUMENTS,
        'pdv_plot_type':
            ['optional',{'choices':['spall','velocity'],'default':'spall',
                         'help':'Type of analysis to perform ("spall" or "velocity")'}],
        'gemd_json_dir':
            ['positional',{'type':existing_dir,
                           'help':'Directory containing all of the GEMD JSON dump files that should be uploaded'}]
    }
