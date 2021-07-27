#imports
from ..data_file_io.data_file_chunk import DataFileChunk
from confluent_kafka.serialization import Serializer, Deserializer
from confluent_kafka.error import SerializationError
from hashlib import sha512
import msgpack, pathlib

####################### SERIALIZING/DESERIALIZING FILE CHUNKS #######################

class DataFileChunkSerializer(Serializer) :

    def __call__(self,file_chunk_obj,ctx=None) :
        if file_chunk_obj is None :
            return None
        elif not isinstance(file_chunk_obj,DataFileChunk) :
            raise SerializationError('ERROR: object passed to FileChunkSerializer is not a DataFileChunk!')
        #pack up all the relevant bits of information into a single bytearray
        try :
            ordered_properties = []
            ordered_properties.append(str(file_chunk_obj.filename))
            ordered_properties.append(file_chunk_obj.file_hash)
            ordered_properties.append(file_chunk_obj.chunk_hash)
            ordered_properties.append(file_chunk_obj.chunk_offset_write)
            ordered_properties.append(file_chunk_obj.chunk_i)
            ordered_properties.append(file_chunk_obj.n_total_chunks)
            ordered_properties.append(file_chunk_obj.subdir_str)
            ordered_properties.append(file_chunk_obj.filename_append)
            ordered_properties.append(file_chunk_obj.data)
            return msgpack.packb(ordered_properties,use_bin_type=True)
        except Exception as e :
            raise SerializationError(f'ERROR: failed to serialize a DataFileChunk! Exception: {e}')

class DataFileChunkDeserializer(Deserializer) :

    def __call__(self,byte_array,ctx=None) :
        if byte_array is None :
            return None
        try :
            #unpack the byte array
            ordered_properties = msgpack.unpackb(byte_array,raw=True)
            if len(ordered_properties)!=9 :
                errmsg = 'ERROR: unrecognized token passed to DataFileChunkDeserializer. Expected 9 properties'
                errmsg+= f' but found {len(ordered_properties)}'
                raise ValueError(errmsg)
            try :
                filename = str(ordered_properties[0].decode())
                file_hash = ordered_properties[1]
                chunk_hash = ordered_properties[2]
                chunk_offset_read = None
                chunk_offset_write = int(ordered_properties[3])
                chunk_i = int(ordered_properties[4])
                n_total_chunks = int(ordered_properties[5])
                subdir_str = str(ordered_properties[6].decode())
                filename_append = str(ordered_properties[7].decode())
                data = ordered_properties[8]
            except Exception as e :
                raise ValueError(f'ERROR: unrecognized value(s) when deserializing a DataFileChunk from token. Exception: {e}')
            #make sure the hash of the chunk's data matches with what it was before
            check_chunk_hash = sha512()
            check_chunk_hash.update(data)
            check_chunk_hash = check_chunk_hash.digest()
            if check_chunk_hash!=chunk_hash :
                errmsg = f'ERROR: chunk hash {check_chunk_hash} != expected hash {chunk_hash} in file {filename}, offset {chunk_offset_write}'
                raise RuntimeError(errmsg)
            #set the filepath based on the subdirectory string
            if subdir_str=='' :
                filepath = pathlib.Path(filename)
            subdir_path = pathlib.PurePosixPath(subdir_str)
            filepath = pathlib.Path('').joinpath(*(subdir_path.parts),filename)
            return DataFileChunk(filepath,filename,file_hash,chunk_hash,chunk_offset_read,chunk_offset_write,
                                 len(data),chunk_i,n_total_chunks,data=data,filename_append=filename_append)
        except Exception as e :
            raise SerializationError(f'ERROR: failed to deserialize a DataFileChunk! Exception: {e}')

