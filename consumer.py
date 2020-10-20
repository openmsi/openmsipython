import uuid

from confluent_kafka import Producer, Consumer




c = Consumer({
    'bootstrap.servers': 'pkc-ep9mm.us-east-2.aws.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '5AZU24G7K7AKNSYS',
    'sasl.password': '6H8nMfsoeqJsoBShvtC5GIWHOS6U8La22JDKrWI2BT8wZWKi8qTTHrC3ygFueC2S',
    'group.id': str(uuid.uuid1()),  # this will create a new consumer group on each invocation.
    'auto.offset.reset': 'earliest'
})

c.subscribe(['users'])

try:
    while True:
        msg = c.poll(0.1)  # Wait for message or event/error
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to `session.timeout.ms` for
            #   the group to rebalance and start consuming.
            continue
        if msg.error():
            # Errors are typically temporary, print error and continue.
            print("Consumer error: {}".format(msg.error()))
            continue
        # write message to file instead of printing
        # print(msg.value())
        filecontents = msg.value().decode()
        file_deliniation = filecontents.split("\n")
        file = open(file_deliniation[0], 'w')
        file.write(filecontents)
        print('consumed: {}'.format(msg.value()))
        
except KeyboardInterrupt:
    pass

finally:
    # Leave group and commit final offsets
    c.close()
