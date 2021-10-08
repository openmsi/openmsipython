#imports
import json, requests, getpass, fmrest
from gemd.json import GEMDJson
from gemd.entity.util import complete_material_history, make_instance
from .laser_shock_sample import LaserShockSample

class LaserShockLab() :
    """
    Representation of all the information in the Laser Shock Lab's FileMaker database in GEMD language
    """

    #################### CONSTANTS AND PROPERTIES ####################

    FILEMAKER_SERVER_IP_ADDRESS = 'https://10.173.38.223'
    DATABASE_NAME = 'Laser Shock'

    #################### PUBLIC METHODS ####################

    def __init__(self) :
        #get login credentials from the user
        self.username = (input('Please enter your JHED username: ')).rstrip()
        self.password = getpass.getpass(f'Please enter the JHED password for {self.username}: ')
        #add all the information to the lab object based on entries in the FileMaker DB
        #self.__add_inventory()
        #self.__add_laser_characteristics()
        #self.__add_flyer_stacks()
        self.samples = self.__get_samples()
        #self.__add_launch_packages()
        #self.__add_experiments()

    def dump_to_json_files(self) :
        """
        Write out different parts of the lab as json files
        """
        #create the encoder
        encoder = GEMDJson()
        #dump the different parts of the lab data model to json files
        with open('laser_shock_sample_spec.json', 'w') as fp:
            fp.write(encoder.thin_dumps(self.samples[0].spec, indent=2))
        with open('example_laser_shock_sample_material_history.json', 'w') as fp :
            context_list = complete_material_history(self.samples[0])
            fp.write(json.dumps(context_list, indent=2))

    #################### PRIVATE HELPER FUNCTIONS ####################

    def __get_filemaker_records(self,layout_name,n_max_records) :
        #disable warnings
        requests.packages.urllib3.disable_warnings()
        #create the server
        fms = fmrest.Server(self.FILEMAKER_SERVER_IP_ADDRESS,
                            user=self.username,
                            password=self.password,
                            database=self.DATABASE_NAME,
                            layout=layout_name,
                            verify_ssl=False,
                           )
        #login
        fms.login()
        #return records in the foundset
        return fms.get_records(limit=n_max_records)

    def __add_inventory(self) :
        pass

    def __add_laser_characteristics(self) :
        pass

    def __add_flyer_stacks(self) :
        pass

    def __get_samples(self) :
        #get records from the FileMaker server
        records = self.__get_filemaker_records('Sample',10)
        return [LaserShockSample(record) for record in records]

    def __add_launch_packages(self) :
        pass

    def __add_experiments(self) :
        pass


#################### MAIN FUNCTION ####################

def main() :
    #build the model of the lab
    model = LaserShockLab()
    #dump its pieces to json files
    model.dump_to_json_files()

if __name__=='__main__' :
    main()
