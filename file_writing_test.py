#!/usr/bin/python3
# This is the files Kafka Consumer
# It consumes data from Kafka file uploaders
# Requires a bunch of stuff installed:
# sudo apt install python3 python3-pip libsodium (sometimes libsodium18)
# sudo pip3 install pysodium msgpack kafka-python confluent_kafka
#
import msgpack
import os
import logging
import traceback
from queue import Queue
from threading import Thread, Lock
from sys import argv
from time import time,sleep
from kafkacrypto import KafkaCrypto, KafkaConsumer, KafkaProducer, KafkaCryptoStore, OffsetAndMetadata
from confluent_kafka import Consumer
import uuid

concurrent_chunks = 10

# Process configuration file


# Setup KafkaCrypto


# program specific configuration
##dead_letter_queue_suffix = kcs.load_value('dead_letter_queue_suffix',default=".dead_letter_queue")
##prefix_depth = kcs.load_value('prefix_depth',default=0)
##prefix_length = kcs.load_value('prefix_length',default=1)
##refresh_time = kcs.load_value('refresh_time',default=300)
##commit_time = kcs.load_value('commit_time',default=5)
##max_reprocess_attempts = kcs.load_value('max_reprocess_attempts',default=5)
##reprocess_delay = kcs.load_value('reprocess_delay',default=2.0)
##concurrent_chunks = kcs.load_value('concurrent_chunks',default=1)
##max_queue_length = kcs.load_value('max_queue_length',default=concurrent_chunks*2)


# process chunk function
def process_chunk():
  global chunk_queue
  n = 1
  while True:
    print("processing chunk ", n, " \n")
    n = n + 1
    token = chunk_queue.get()
    if token is None:
      break
    token = msgpack.unpackb(token, raw=True)
##      topic_dir = token[0].rsplit("/")[0]
##      file_name = "/output/"
##      if not os.path.exists(topic_dir):
##        os.makedirs(topic_dir)
    if len(token) == 6:
      file = "/home/sam/Desktop/test-directory/" + "/" + token[5].decode()
      print(token[4].decode())
      #with open(os.path.join(topic_dir,file_name), "rb+", opener=lambda a,b: os.open(a,b|os.O_CREAT)) as f:
      with open(file, "w") as f:
         f.seek(token[3],0)
         f.write(token[4].decode())
         f.flush()
         os.fsync(f.fileno())
         f.close()
      chunk_queue.task_done()
    

# setup chunk queue and chunk processing threads
# no limit here on queue size to avoid a deadlock between threads
chunk_queue = Queue()
chunk_threads = []
for i in range(concurrent_chunks):
  t = Thread(target=process_chunk)
  t.daemon = True
  t.start()
  chunk_threads.append(t)


consumer = Consumer({
    'bootstrap.servers': 'pkc-ep9mm.us-east-2.aws.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '5AZU24G7K7AKNSYS',
    'sasl.password': '6H8nMfsoeqJsoBShvtC5GIWHOS6U8La22JDKrWI2BT8wZWKi8qTTHrC3ygFueC2S',
    'group.id': str(uuid.uuid1()),  # this will create a new consumer group on each invocation.
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['lecroy_files'])

while True:
  msg = consumer.poll()
  chunk_queue.put(msg.value())
  


# Setup Kafka
##kafka_config = kcs.get_kafka_config('consumer')
##kafka_config['key_deserializer'] = kc.getKeyDeserializer()
##kafka_config['value_deserializer'] = kc.getValueDeserializer()
##if (not ('enable_auto_commit' in kafka_config.keys())) or kafka_config['enable_auto_commit'] != False:
##  logging.warning('enable_auto_commit is not disabled. Consumer may mark messages written when they are not.')
##consumer = KafkaConsumer(**kafka_config)
##kafka_config = kcs.get_kafka_config('producer')
##kafka_config['key_serializer'] = kc.getKeySerializer()
##kafka_config['value_serializer'] = kc.getValueSerializer()
##producer = KafkaProducer(**kafka_config)
##
##last_refresh = time()
##last_commit = time()
##consumer.subscribe(topics)
##
##num_processed = 0
##unprocessed_offsets = {}
##unprocessed_offsets_last = {}
##unprocessed_offsets_lock = Lock()
##while True:
##  rv = consumer.poll(timeout_ms=commit_time*1000)
##  for tp,msgs in rv.items():
##    for msg in msgs:
##      num_processed += 1
##      logging.debug("Processing message %i", num_processed)
##      if (num_processed % 100 == 0):
##        logging.warning("Processed %i messages", num_processed)
##        chunk_threads = list(filter(lambda a: a.is_alive(), chunk_threads))
##        logging.warning("Using %i writers for %i chunks", len(chunk_threads), chunk_queue.qsize())
##      root = kc.get_root(msg.topic)
##      logging.debug("Received message for root=%s", root)
##      with unprocessed_offsets_lock:
##        if not (tp in unprocessed_offsets.keys()):
##          unprocessed_offsets[tp] = {}
##        unprocessed_offsets[tp][msg.offset] = OffsetAndMetadata(msg.offset,None)
##        if not (tp in unprocessed_offsets_last.keys()) or msg.offset+1 > unprocessed_offsets_last[tp].offset:
##          unprocessed_offsets_last[tp] = OffsetAndMetadata(msg.offset+1,None)
##      # This is a soft limit to keep the queue (and hence memory usage) from growing in an unbounded fashion,
##      # while still allowing threads the ability to cycle through the queue and make progress as decryption
##      # keys become available.
##      while chunk_queue.qsize() > max_queue_length:
##        sleep(0.5)
##      chunk_queue.put([tp, msg.offset, topics_dirs[root], msg.value, time(), 0])
##  if last_commit+commit_time<time():
##    logging.debug("Finding Committable Offsets")
##    tocommit = {}
##    with unprocessed_offsets_lock:
##      for tp in unprocessed_offsets.keys():
##        if len(unprocessed_offsets[tp].keys()) > 0:
##          tocommit[tp] = unprocessed_offsets[tp][min(unprocessed_offsets[tp].keys())]
##        else:
##          tocommit[tp] = unprocessed_offsets_last[tp]
##    if len(tocommit) > 0:
##      logging.debug("Commiting Offsets")
##      consumer.commit(offsets=tocommit)
##    else:
##      logging.debug("Nothing to Commit")
##    last_commit = time()
##  if (last_refresh+refresh_time < time()):
##    last_refresh = time()
##    consumer.subscribe(topics)
##  # for dead letters
##  producer.poll()
