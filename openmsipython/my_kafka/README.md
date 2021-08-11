## More details on configuration files

All available programs depend on configuration files to define which kafka clusters they should connect to and how they should produce to/consume from topics in those clusters. This section gives a few more details about how these files can be formatted, the recognized sections they can contain, and options you can change using them.

In general, a configuration file is a text file with one or more distinct and named sections. Comments can be added by using lines starting with "`#`", and other whitespace in general is ignored. Each section begins with a heading line like "`[section_name]`" (with square brackets included), and beneath that heading different parameters are supplied using lines like "`key = value`". If any parameter `value`s begin with the "`$`" character, the configuration file parser will attempt to expand those values as environment variables (this is useful to, for example, store usernames or passwords as environment variables instead of plain text in the repository).

The different sections recognized by the `openmsipython` code are:
1. `[cluster]` to configure which Kafka cluster should be used by a program and how to connect to it. Common parameters here include:
    - `bootstrap.servers` to detail the server on which the cluster is hosted
    - `sasl.mechanism` and `security.protocol` to describe how programs are authenticated to interact with the cluster
    - `sasl.username` and `sasl.password` to provide the key and secret of an API key created for the cluster
1. `[producer]` to configure a Producer used by a program. You can add here any [parameters recognized by Kafka Producers](https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html) in general, but some of the most useful are:
    - `batch.size` to control the maximum number of messages in each batch sent to the cluster
    - `retries` to control how many times a failed message should be retried before throwing a fatal error and moving on
    - `linger.ms` to change how long a batch of messages should wait to become as full as possible before being sent to the cluster 
    - `compression.type` to add or change how batches of messages are compressed before being produced (and decompressed afterward)
    - `key.serializer` and `value.serializer` to change methods used to convert message keys and values (respectively) to byte arrays. The `openmsipython` code provides an additional option called [`DataFileChunkSerializer`](./serialization.py#L10-#L31) as a message value serializer to pack chunks of data files.
1. `[consumer]` to configure a Consumer used by a program. Again here any [parameters recognized by Kafka Consumers](https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html) in general are valid, but some of the most useful are:
    - `group.id` to group Consumers amongst one another. Giving "`new`" for this parameter will create a new group ID every time the code is run.
    - `auto.offset.reset` to tell the Consumer where in the log to start consuming messages if no previously-committed offset for the consumer group can be found. "`earliest`" will start at the beginning of the topic and "`latest`" will start at the end. Giving "`none`" for this parameter will remove it from the configs, and an error will be thrown if no previously-committed offset for the consumer group can be found.
    - `fetch.min.bytes` to change how many bytes must accumulate before a batch of messages is consumed from the topic (consuming batches of messages is also subject to a timeout, so changing this parameter will only ever adjust the tradeoff between throughput and latency, but will not prevent any messages from being consumed in general)
    - `key.deserializer` and `value.deserializer` to change methods used to convert message keys and values (respectively) from byte arrays to objects. The `openmsipython` code provides an additional option called [`DataFileChunkDeserializer`](./serialization.py#L33-#L75) to convert a chunk of a data file as a byte array to a [DataFileChunk object](./openmsipython/data_file_io/data_file_chunk.py#L7).
