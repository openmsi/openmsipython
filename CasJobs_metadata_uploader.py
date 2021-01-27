from queue import Queue
from threading import Thread, Lock
from time import sleep
from socket import socket, AF_INET, SOCK_STREAM, timeout
from confluent_kafka import Consumer, Producer
from sys import argv
from hashlib import sha512
import pysodium
import msgpack
import logging
import traceback
import os
import uuid
from itertools import islice
from SciServer import CasJobs
from SciServer import Authentication

username = "sjtabs"
password = "Tig2barlpw"

token = Authentication.login(username, password)

user = Authentication.getKeystoneUserWithToken(token)

#csv = open("./metadata_table.csv", 'r')
#csv_str = csv.read()
#csv.close()

#success = CasJobs.uploadCSVDataToTable(csv_str, "osc_metadata")

#print(success)


query1 = "create table osc_metadata (FileName varchar(255), FileSize varchar(255))"
CasJobs.executeQuery(sql=query1,format='json')

# get file name and size
f = argv[1]
f_name = os.path.basename(f)
f_size = os.path.getsize(f)

print(f_name)

print(f_size)

# upload data to table
query2 = "insert into osc_metadata (FileName, FileSize) values (" + "'" + f_name[0:2] + "''" + f_name[2:3] + "''" + f_name[3:12] + "''" + f_name[12] + "''" + f_name[13:] + "'" + ", " + "'" + str(f_size) + "'" + ")"


CasJobs.executeQuery(sql=query2,format='json')
