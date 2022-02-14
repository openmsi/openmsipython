#imports
import unittest, pathlib, logging, pickle, shutil
from openmsipython.shared.logging import Logger
from openmsipython.data_models.laser_shock.laser_shock_lab import LaserShockLab
from config import TEST_CONST

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestLaserShockLabGEMD(unittest.TestCase) :
    """
    Class for testing creation of Laser Shock Lab GEMD objects from the FileMaker Database
    (or, truthfully, a dump of a few of its records)
    """

    def test_laser_shock_lab_gemd(self) :
        #create the Laser Shock Lab object
        output_dir = pathlib.Path(__file__).parent/TEST_CONST.LASER_SHOCK_DATA_MODEL_OUTPUT_DIRNAME
        lab = LaserShockLab(working_dir=output_dir,logger=LOGGER)
        #read in the test record dictionary
        with open(TEST_CONST.TEST_DATA_DIR_PATH/TEST_CONST.FILEMAKER_RECORD_PICKLE_FILENAME,'rb') as fp :
            filemaker_record_dict = pickle.load(fp)
        #create GEMD objects from the dictionary
        lab.create_gemd_objects(records_dict=filemaker_record_dict)
        #dump the GEMD objects to JSON files
        lab.dump_to_json_files(complete_histories=True,recursive=False)
        #compare the new files with those in the reference directory
        try :
            for fp in (TEST_CONST.TEST_DATA_DIR_PATH/TEST_CONST.LASER_SHOCK_DATA_MODEL_OUTPUT_DIRNAME).glob('*.json') :
                self.assertTrue((output_dir/fp.name).is_file())
                with open(fp,'r') as ref_fp :
                    ref_lines = ref_fp.readlines()
                with open(output_dir/fp.name,'r') as new_fp :
                    new_lines = new_fp.readlines()
                self.assertTrue(len(new_lines)==len(ref_lines))
                for rl,nl in zip(ref_lines,new_lines) :
                    #skip lines corresponding to uids
                    if (rl.lstrip()).startswith('"id": "') or (rl.lstrip()).startswith('"auto": "') :
                        continue
                    self.assertEqual(rl,nl)
        except Exception as e :
            raise e
        finally :
            shutil.rmtree(output_dir)

