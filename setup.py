#imports
import setuptools, site

site.ENABLE_USER_SITE = True #https://www.scivision.dev/python-pip-devel-user-install/

setuptools.setup(
    name='openmsipython',
    version='0.0.1',
    packages=setuptools.find_packages(include=['openmsipython*']),
    include_package_data=True,
    entry_points = {
        'console_scripts' : ['manage_service=openmsipython.command_line_scripts.manage_service:main',
                             'upload_data_files_added_to_directory=openmsipython.command_line_scripts.upload_data_files_added_to_directory:main',
                             'upload_data_file=openmsipython.command_line_scripts.upload_data_file:main',
                             'reconstruct_data_files=openmsipython.command_line_scripts.reconstruct_data_files:main',
                            ],
    },
    python_requires='>=3.7,<3.8',
    install_requires=['confluent-kafka>=1.6.0',
                      'msgpack>=1.0.0',
                     ],
    extras_require = {'test': ['pyflakes>=2.2.0',],},
)