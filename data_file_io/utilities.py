#Several utility functions used in a few different places

#imports
from threading import Thread, Lock

#a helper function to produce every file chunk in a given queue to the given topic using the given producer
def produce_queue_of_file_chunks(queue,producer,topic_name,n_threads,logger) :
    #upload all the file chunks in the queue in parallel threads
    upload_threads = []
    file_chunk = queue.get()
    lock = Lock()
    while file_chunk is not None :
        t = Thread(target=file_chunk.upload_as_message,args=(producer,
                                                             topic_name,
                                                             logger,
                                                             lock,))
        t.start()
        upload_threads.append(t)
        if len(upload_threads)>=n_threads :
            for ut in upload_threads :
                ut.join()
            upload_threads = []
        file_chunk = queue.get()
    for ut in upload_threads :
        ut.join()
    logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
    producer.flush() #don't leave the function until all messages have been sent/received
    logger.info('Done!')