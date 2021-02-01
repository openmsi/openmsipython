#imports
from .logging import Logger
from hashlib import sha512
import dataclasses
import msgpack

#utility class holding information for a single chunk of a leCroy file 
@dataclasses.dataclass
class LeCroyFileChunkInfo :
    filepath : str
    file_hash : str
    chunk_hash : str
    chunk_offset : int
    chunk_size : int
    filename : str

    #return the file chunk as a packed message
    def packed_as_msg_with_data(self,data) :
        p_list = []
        p_list.append(self.filepath)
        p_list.append(self.file_hash)
        p_list.append(self.chunk_hash)
        p_list.append(self.chunk_offset)
        p_list.append(data)
        p_list.append(self.filename)
        return msgpack.packb(p_list,use_bin_type=True)

#upload a single LeCroyFileChunkInfo token with its data to a given topic (meant to be run in parallel)
def upload_lecroy_file_chunk_worker(token,token_i,n_tokens,producer,topic_name,logger=None,print_every=1000) :
    if logger is None :
        logger = Logger()
    filepath = token.filepath
    if (token_i-1)%print_every==0 :
        logger.info(f'uploading {filepath} chunk {token_i} (out of {n_tokens})')
    chunk_hash = token.chunk_hash
    chunk_offset = token.chunk_offset
    chunk_len = token.chunk_size
    #get this chunk's data from the file
    with open(filepath, "rb") as fp:
        fp.seek(chunk_offset)
        data = fp.read(chunk_len)
    #make sure it's of the expected size
    if len(data) != chunk_len:
        msg = f'ERROR: chunk {chunk_hash} size {len(data)} != expected size {chunk_len} in file {filepath}, offset {chunk_offset}'
        logger.error(msg,ValueError)
    check_chunk_hash = sha512()
    check_chunk_hash.update(data)
    check_chunk_hash = check_chunk_hash.digest()
    if chunk_hash != check_chunk_hash:
        msg = f'ERROR: chunk hash {check_chunk_hash} != expected hash {chunk_hash} in file {filepath}, offset {chunk_offset}'
        logger.error(msg,ValueError)
    producer.produce(topic=topic_name,value=token.packed_as_msg_with_data(data))
    producer.poll(0)