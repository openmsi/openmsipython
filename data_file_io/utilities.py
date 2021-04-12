#Several utility functions

#a helper function to produce every file chunk in a given queue to the given topic using the given producer
def produce_from_queue_of_file_chunks(queue,producer,topic_name,logger) :
    #upload all the file chunks in the queue in a single thread
    file_chunk = queue.get()
    while file_chunk is not None :
        file_chunk.upload_as_message(producer,topic_name,logger)
        queue.task_done()
        file_chunk = queue.get()
    queue.task_done()
