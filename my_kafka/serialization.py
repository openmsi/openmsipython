#imports
from ..data_file_io.data_file_chunk import DataFileChunk
from confluent_kafka.serialization import Serializer, Deserializer
from confluent_kafka.error import SerializationError
from hashlib import sha512
import pathlib, msgpack

####################### SERIALIZING/DESERIALIZING FILE CHUNKS #######################

class DataFileChunkSerializer(Serializer) :

    def __call__(self,file_chunk_obj,ctx) :
        if file_chunk_obj is None :
            return None
        elif not isinstance(file_chunk_obj,DataFileChunk) :
            raise SerializationError('ERROR: object passed to FileChunkSerializer is not a DataFileChunk!')
        try :
            ordered_properties = []
            ordered_properties.append(str(file_chunk_obj.filepath))
            ordered_properties.append(file_chunk_obj.file_hash)
            ordered_properties.append(file_chunk_obj.chunk_hash)
            ordered_properties.append(file_chunk_obj.chunk_offset)
            ordered_properties.append(file_chunk_obj.chunk_i)
            ordered_properties.append(file_chunk_obj.n_total_chunks)
            ordered_properties.append(file_chunk_obj.data)
            return msgpack.packb(ordered_properties,use_bin_type=True)
        except Exception as e :
            raise SerializationError(f'ERROR: failed to serialize a DataFileChunk! Exception: {e}')

class DataFileChunkDeserializer(Deserializer) :

    def __call__(self,byte_array,ctx) :
        if byte_array is None :
            return None
        try :
            ordered_properties = msgpack.unpackb(byte_array,raw=True)
            if len(ordered_properties)!=7 :
                raise ValueError(f'ERROR: unrecognized token passed to FileChunkDeserializer. Expected 7 properties but found {len(ordered_properties)}')
            try :
                filepath = pathlib.Path(str(ordered_properties[0].decode()))
                file_hash = ordered_properties[1]
                chunk_hash = ordered_properties[2]
                chunk_offset = int(ordered_properties[3])
                chunk_i = int(ordered_properties[4])
                n_total_chunks = int(ordered_properties[5])
                data = ordered_properties[6]
            except Exception as e :
                raise ValueError(f'ERROR: unrecognized value(s) when deserializing a DataFileChunk from token. Exception: {e}')
            check_chunk_hash = sha512()
            check_chunk_hash.update(data)
            check_chunk_hash = check_chunk_hash.digest()
            if check_chunk_hash!=chunk_hash :
                raise RuntimeError(f'ERROR: chunk hash {check_chunk_hash} != expected hash {chunk_hash} in file {filepath}, offset {chunk_offset}')
            return DataFileChunk(filepath,file_hash,chunk_hash,chunk_offset,len(data),chunk_i,n_total_chunks,data)
        except Exception as e :
            raise SerializationError(f'ERROR: failed to deserialize a DataFileChunk! Exception: {e}')

