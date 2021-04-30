#imports
import pathlib, time

#every 5 seconds, create a new file in the specified directory, up to 100 files
filedirpath = pathlib.Path('D:\\meminizer\\service_test_dir')
if not filedirpath.is_dir() :
	filedirpath.mkdir()
for i in range(100) :
	filename = f'service_test_{i+1}.txt'
	with open(filedirpath / filename) as fp :
		fp.write(f'hello in file number {i+1} : )')
