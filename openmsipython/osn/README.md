### OSN_MSI General information
The Open Storage Network (OSN) is intended for data integrity coming from different labs through kafka-streaming into corresponding objects.
###OSN_MSI
This module uploads data from streaming-consumer into OSN directly.

###OSN_MSI Command Line and Environmental Configuration
There are different approaches that data could be sent into OSN. In this particular module we send data through s3Client. Therefore, we will need to access the following information:

i. Environmental Configuration, under [osn]:
   1) access_key_id ($ACCESS_SECRET_KEY_ID)
   2) secret_key_id ($SECRET_KEY_ID)
   3) endpoint_url ($ENDPOINT_URL)
   4) region ($REGION)

The above items from 1-4, need to be set up in your local environmental machine. 

ii. Command Line:
   5) logger_file path (optional)
   6) bucket_name
   7) config file (optional)
   8) topic_name

Optional: As this module interacts with consumer, it requires to log events somewhere in your local machine. If you do not specify a folder for that, the module would save the log file in the root folder,
otherwise, you may specify a directory for the log file, and it should be take place as a first command.

The bucket_name needs to be entered in your command line as the first command. 
Optional: If you are willing to address your configuration, you will need to add '--config' and then after path of your config file.
You will also need to address the name of your topic in the command line (as this module consumes data from a specific topic). 

Example of a command line with optional commands:
args = ['C:\\osn_data', 'bucket01', '--config', 'C:\\config_files\\test.config', '--topic_name', 'topic_1']

Example of a command line without optional commands:
args = ['bucket01', '--config', '--topic_name', 'topic_1']
