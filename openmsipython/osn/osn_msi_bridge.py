# @author: Amir H. Sharifzadeh, https://pages.jh.edu/asharif9/
# @project: OpenMSI
# @date: 04/13/2022
# @owner: The Institute of Data Intensive Engineering and Science, https://idies.jhu.edu/
# Johns Hopkins University http://www.jhu.edu/

import time
import threading

from openmsipython.data_file_io.data_file_download_directory import DataFileDownloadDirectory
from openmsipython.osn.s3_data_transfer import s3_data_transfer


class osn_msi_bridge:
    def __init__(self, args):
        self.args = args

    def download_open_msi_command(self):
        print("Downloading files from topic")
        DataFileDownloadDirectory.run_from_command_line(self.args)

    def upload_osn_s3_command(self):
        print("Uploading files into OSN")
        while True:
            s3d = s3_data_transfer()
            s3d.transfer_object()
            time.sleep(1)

    def execute_command(self):
        th1 = threading.Thread(target=self.download_open_msi_command)
        th2 = threading.Thread(target=self.upload_osn_s3_command)

        th1.start()
        th2.start()
        th1.join()
        th2.join()


def main(args=None) :
    omb = osn_msi_bridge(args)
    omb.execute_command()

if __name__=='__main__' :
    main()
