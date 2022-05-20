# @author: Amir H. Sharifzadeh, https://pages.jh.edu/asharif9/
# @project: OpenMSI
# @date: 04/12/2022
# @owner: The Institute of Data Intensive Engineering and Science, https://idies.jhu.edu/
# Johns Hopkins University http://www.jhu.edu

from botocore.exceptions import ClientError
from ..shared.logging import LogOwner
from .osn_service import OSNService

class S3DataTransfer(OSNService,LogOwner) :

    def __init__(self, osn_config):
        super().__init__(osn_config)

    def transfer_object_stream(self, datafile):
        file_name = str(datafile.filename)
        sub_dir=datafile.get_subdir_str
        osn_full_path = sub_dir + '/' + file_name

        try:
            self.s3_client.put_object(Body=datafile.bytestring, Bucket=self.bucket_name,
                                      Key=osn_full_path, GrantRead=self.grant_read)
            logging.info(file_name + ' successfully transferred into /' + sub_dir)
        except ClientError as e:
            logging.error(e.response + ': failed to transfer ' + file_name + ' into /'
                          + sub_dir)

#    def transfer_object_file(self):
#        local_path_list = []
#        for root, subdirectories, files in os.walk(OSN_DOWNLOAD):
#            for file in files:
#                if file == 'DataFileDownloadDirectory.log':
#                    continue
#
#                my_root = str(root)
#
#                s3_path = os.path.join(my_root, file).replace(OSN_DOWNLOAD, '').replace('\\', '/')
#                if '/' in s3_path:
#                    m = s3_path.rindex('/')
#                    s3_dir = s3_path[0:m]
#                else:
#                    s3_dir = ''
#
#                print(s3_dir)
#                if len(s3_dir) > 0 and s3_dir not in local_path_list:
#                    local_path_list.append(s3_dir)
#                    self.s3_client.put_object(Bucket=BUCKET_NAME, Key=(s3_dir + '/'))
#
#                local_path = os.path.join(my_root, file).replace('/', '\\')
#                print(local_path)
#                try:
#                    if len(s3_dir) == 0:
#                        self.s3_client.upload_file(local_path, BUCKET_NAME, str(file))
#                    else:
#                        self.s3_client.upload_file(local_path, BUCKET_NAME, '%s/%s' % (str(s3_dir), str(file)))
#                    os.remove(local_path)
#                except ClientError as e:
#                    print(e.response)
