import uuid
import time

from confluent_kafka import Producer, Consumer


p = Producer({
    'bootstrap.servers': 'pkc-ep9mm.us-east-2.aws.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '5AZU24G7K7AKNSYS',
    'sasl.password': '6H8nMfsoeqJsoBShvtC5GIWHOS6U8La22JDKrWI2BT8wZWKi8qTTHrC3ygFueC2S'
})


def acked(err, msg):
    """Delivery report callback called (from flush()) on successful or failed delivery of the message."""
    if err is not None:
        print("failed to deliver message: {}".format(err.str()))
    else:
        print("produced to: {} [{}] @ {}".format(msg.topic(), msg.partition(), msg.offset()))

while True:
    # filename = input("Enter file name ")
    filename = "/home/sam/Desktop/test_file"
    with open(filename, 'r') as file:
        data = file.read()
    data = data.encode()
    p.produce('users', value = data, callback=acked)
    time.sleep(2)
# flush() is typically called when the producer is done sending messages to wait
# for outstanding messages to be transmitted to the broker and delivery report
# callbacks to get called. For continous producing you should call p.poll(0)
# after each produce() call to trigger delivery report callbacks.
p.flush(10)
