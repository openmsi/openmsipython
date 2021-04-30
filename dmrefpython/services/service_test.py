#imports
import pathlib, time

#every 5 seconds, create a new file in the specified directory, up to some number of files
filedirpath = pathlib.Path('D:\\meminizer\\service_test_dir')
if not filedirpath.is_dir() :
	filedirpath.mkdir()
n_files = 20
for i in range(n_files) :
	filename = f'service_test_{i+1}_of_{n_files}.txt'
	with open(filedirpath / filename,'w') as fp :
		fp.write(f'hello in file number {i+1} of {n_files} : )')
	time.sleep(5)
