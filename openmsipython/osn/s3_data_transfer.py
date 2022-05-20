# @author: Amir H. Sharifzadeh, https://pages.jh.edu/asharif9/
# @project: OpenMSI
# @date: 04/12/2022
# @owner: The Institute of Data Intensive Engineering and Science, https://idies.jhu.edu/
# Johns Hopkins University http://www.jhu.edu
from openmsipython.shared.logging import Logger
from botocore.exceptions import ClientError
from openmsipython.osn.osn_service import osn_service


class s3_data_transfer(osn_service):
    def __init__(self, osn_config):
        super().__init__(osn_config)

    def transfer_object_stream(self, topic_name,datafile):
        file_name = str(datafile.filename)
        sub_dir=datafile.get_subdir_str
        osn_full_path = topic_name + '/' + sub_dir + '/' + file_name

        try:
            self.s3_client.put_object(Body=datafile.bytestring, Bucket=self.bucket_name,
                                      Key=osn_full_path
                                      # , GrantRead=self.grant_read
                                      )
            Logger.info(file_name + ' successfully transferred into /' + sub_dir)
        except ClientError as e:
            Logger.error(e.response + ': failed to transfer ' + file_name + ' into /'
                          + sub_dir)

    def find_by_object_key(self, key):
        return super().find_by_object_key(key)

    def get_object_stream_by_osn_datafile(self, topic_name, bucket_name, datafile):
        return super().get_object_stream_by_osn_datafile(topic_name, bucket_name, datafile)

    def get_object_stream_by_object_key(self, bucket_name, object_key):
        return super().get_object_stream_by_object_key(bucket_name, object_key)

    def compare_consumer_datafile_with_osn_object_stream(self, topic_name, bucket_name, datafile):
        return super().compare_consumer_datafile_with_osn_object_stream(topic_name, bucket_name, datafile)

    def compare_producer_datafile_with_osn_object_stream(self, bucket_name, object_key, hashed_datafile_stream):
        return super().compare_producer_datafile_with_osn_object_stream(bucket_name, object_key, hashed_datafile_stream)

    def delete_object_from_osn(self, bucket_name, object_key):
        return super().delete_object_from_osn(bucket_name, object_key)