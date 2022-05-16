# @author: Amir H. Sharifzadeh, https://pages.jh.edu/asharif9/
# @project: OpenMSI
# @date: 04/12/2022
# @owner: The Institute of Data Intensive Engineering and Science, https://idies.jhu.edu/
# Johns Hopkins University http://www.jhu.edu/

import boto3

class osn_service(object):
    def __init__(self, osn_config):
        self.session = boto3.session.Session()
        self.bucket_name = osn_config['bucket_name']
        self.s3_client = self.session.client(
            service_name='s3',
            aws_access_key_id=osn_config['access_key_id'],
            aws_secret_access_key=osn_config['secret_key_id'],
            region_name=osn_config['region'],
            endpoint_url=osn_config['endpoint_url']
        )
        self.grant_read = 'uri="http://acs.amazonaws.com/groups/global/AllUsers"'