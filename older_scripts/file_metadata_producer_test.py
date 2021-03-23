from queue import Queue
from threading import Thread, Lock
from time import sleep
from socket import socket, AF_INET, SOCK_STREAM, timeout
from kafkacrypto import KafkaCryptoStore, KafkaConsumer, KafkaProducer, KafkaCrypto
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
chunk_size = 4096
concurrent_chunks = 10
upload_queue = Queue()

#os.path.isfile
consumer = Consumer({
    'bootstrap.servers': 'pkc-ep9mm.us-east-2.aws.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '5AZU24G7K7AKNSYS',
    'sasl.password': '6H8nMfsoeqJsoBShvtC5GIWHOS6U8La22JDKrWI2BT8wZWKi8qTTHrC3ygFueC2S',
    'group.id': str(uuid.uuid1()),  # this will create a new consumer group on each invocation.
    'auto.offset.reset': 'earliest'
})


producer = Producer({
    'bootstrap.servers': 'pkc-ep9mm.us-east-2.aws.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '5AZU24G7K7AKNSYS',
    'sasl.password': '6H8nMfsoeqJsoBShvtC5GIWHOS6U8La22JDKrWI2BT8wZWKi8qTTHrC3ygFueC2S'
})


#
# This function is run in its own thread to do all processing associated
# with preparing an upload of a new file, and does everything except upload
# the chunks and metadata themselves, which is handled by a queue.
#


def upload_file_metadata(file):
    global kcs, chunk_size, upload_queue
    #
    # Construct the chain of chunks necessary for this new file.
    #
    fields = []
    file_name = file.rsplit('/')[-1]
    with open(file, "r") as f:
        metadata_lines = list(islice(f, 5))
        for i in range(5):
            fields.append(metadata_lines[i].split(','))
            

    #
    # Now write values to file for future uploading. We do metadata last.
    #
##    kvs = []
##    for c in chunks:
##        kvs.append([c[0],msgpack.packb([file,file_hash,c[0],c[1],c[2]], use_bin_type=True)])
    #
    # And add to upload queue
    #
    upload_queue.put(file_name, fields)
    #upload_queue.put(['metadata',file_hash])
  #
  # Inform client of location
  #
##  with toreply_lock:
##    if (root_data_url != None):
##      toreply.append(file + " at " + root_data_url + file_hash.hex())
##    else:
##      toreply.append(file + " at " + file_hash.hex())


def upload_worker():
    n = 1
    while True:
        global upload_queue
        token = upload_queue.get()
       # file_name = input("Input file name \n")
        if token is None:
            break
            print("all done")
        else:
            file_name = token[0]
            fields = token[1]
            producer.produce(topic='lecroy_files',value=msgpack.packb(['metadata', token[0], token[1]], use_bin_type=True))
            producer.poll(0)

file = input("input file path \n")


upload_file_metadata(file)

upload_threads = []
for i in range(concurrent_chunks):
  t = Thread(target=upload_worker)
  t.daemon = True
  t.start()
  upload_threads.append(t)

##upload_worker()

### Open local server for commands
##conn = socket(AF_INET, SOCK_STREAM)
##conn.bind(('localhost',listen_port))
##conn.listen(1)
##
### Enter processing loop
##threads = []
##try:
##  while True:
##    client,_ = conn.accept()
##    try:
##      client.settimeout(2.0)
##      cmd = ''
##      cmd_part = ''
##      metadata = {}
##      while cmd_part != None:
##        threads = list(filter(lambda a: a.is_alive(), threads))
##        if len(threads) > 0:
##          logging.info("Currently %i files being prepared for upload.", len(threads))
##        upload_threads = list(filter(lambda a: a.is_alive(), upload_threads))
##        if not upload_queue.empty():
##          logging.info("Currently %i chunks and metadata left to upload by %i workers.", upload_queue.qsize(), len(upload_threads))
##        if len(threads) == 0 and upload_queue.empty():
##          logging.info("No current uploads.")
##        while cmd_part != None and cmd.find('\r') == -1 and cmd.find('\n') == -1:
##          try:
##            with toreply_lock:
##              for reply in toreply:
##                if (isinstance(reply,(str))):
##                  client.send(reply.encode('utf-8'))
##                else:
##                  client.send(reply)
##              toreply = []
##            cmd_part = client.recv(4096).decode('utf-8')
##            if len(cmd_part) == 0:
##              cmd_part = None
##          except timeout:
##            cmd_part = ""
##          if cmd_part != None:
##            cmd += cmd_part
##        lines = cmd.splitlines()
##        if not cmd.endswith('\r') and not cmd.endswith('\n') and len(lines) > 0:
##          # last entry is a partial line, remove it and save for next time
##          cmd = lines.pop()
##        else:
##          cmd = ''
##        for l in lines:
##          sl = l.strip()
##          if sl.lower().startswith('upload') and len(sl) > 7:
##            file = sl[7:]
##            logging.info("Uploading %s", file)
##            # dispatch new thread for processing
##            ut = Thread(target=upload_file, args=(file,metadata))
##            ut.daemon = True
##            ut.start()
##            threads.append(ut)
##            metadata = {}
##          elif sl.lower().startswith('metadata') and sl.find('=') != -1:
##            bp = sl.find('=')
##            if bp>9 and bp+1<len(l):
##              lhs = sl[9:bp].strip()
##              rhs = sl[bp+1:].strip()
##              if len(lhs) > 0:
##                if len(rhs) > 0:
##                  metadata[lhs] = rhs
##                else:
##                  metadata.pop(lhs,None)
##              else:
##                logging.warning("Invalid metadata key in command %s", sl)
##            else:
##              logging.warning("Invalid metadata command %s", sl)
##          elif len(sl) > 0:
##            logging.warning("Unknown Command: %s",sl)
##    finally:
##      client.close()
##finally:
##  conn.close()
