# @author: Amir H. Sharifzadeh, https://pages.jh.edu/asharif9/
# @project: OpenMSI
# @date: 04/12/2022
# @owner: The Institute of Data Intensive Engineering and Science, https://idies.jhu.edu/
# Johns Hopkins University http://www.jhu.edu/

import boto3

from openmsipython.osn.OSN_CONSTANTS import ACCESS_KEY_ID, SECRET_KEY_ID, REGION, ENDPOINT_URL

class osn_service(object):
    def __init__(self):
        self.session = boto3.session.Session()
        self.s3_client = self.session.client(
            service_name='s3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_KEY_ID,
            region_name=REGION,
            endpoint_url=ENDPOINT_URL,
        )