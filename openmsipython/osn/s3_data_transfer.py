# @author: Amir H. Sharifzadeh, https://pages.jh.edu/asharif9/
# @project: OpenMSI
# @date: 04/12/2022
# @owner: The Institute of Data Intensive Engineering and Science, https://idies.jhu.edu/
# Johns Hopkins University http://www.jhu.edu

import os
from botocore.exceptions import ClientError

from openmsipython.osn.OSN_CONSTANTS import BUCKET_NAME, \
    OSN_DOWNLOAD
from openmsipython.osn.osn_service import osn_service


class s3_data_transfer(osn_service):
    def __init__(self):
        super().__init__()


    def transfer_object(self):
        # print(self.s3_client.list_buckets())
        local_path_list = []
        for root, subdirectories, files in os.walk(OSN_DOWNLOAD):
            for file in files:
                if file == 'DataFileDownloadDirectory.log':
                    continue

                my_root = str(root)

                s3_path = os.path.join(my_root, file).replace(OSN_DOWNLOAD, '').replace('\\', '/')
                if '/' in s3_path:
                    m = s3_path.rindex('/')
                    s3_dir = s3_path[0:m]
                else:
                    s3_dir = ''

                print(s3_dir)
                if len(s3_dir) > 0 and s3_dir not in local_path_list:
                    local_path_list.append(s3_dir)
                    self.s3_client.put_object(Bucket=BUCKET_NAME, Key=(s3_dir + '/'))

                local_path = os.path.join(my_root, file).replace('/', '\\')
                print(local_path)
                try:
                    if len(s3_dir) == 0:
                        self.s3_client.upload_file(local_path, BUCKET_NAME, str(file))
                    else:
                        self.s3_client.upload_file(local_path, BUCKET_NAME, '%s/%s' % (str(s3_dir), str(file)))
                    os.remove(local_path)
                except ClientError as e:
                    print(e.response)

if __name__ == '__main__':
    s3d = s3_data_transfer()
    s3d.transfer_object()
