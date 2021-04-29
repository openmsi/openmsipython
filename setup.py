#imports
import setuptools, site

site.ENABLE_USER_SITE = True #https://www.scivision.dev/python-pip-devel-user-install/

setuptools.setup(
    name='dmrefpython',
    version='0.0.1',
    packages=setuptools.find_packages(include=['dmrefpython*']),
    entry_points = {
        'console_scripts' : ['upload_data_files_added_to_directory=dmrefpython.command_line_scripts.upload_data_files_added_to_directory:main',
                             'upload_data_file=dmrefpython.command_line_scripts.upload_data_file:main',
                             'reconstruct_data_files=dmrefpython.command_line_scripts.reconstruct_data_files:main',
                            ],
    },
    python_requires='>=3.7',
    install_requires=['confluent-kafka>=1.6.0',
                      'msgpack>=1.0.0',
                     ],
    extras_require={
        'windows_services':['pywin32',],
    }
)