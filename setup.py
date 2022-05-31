#imports
import setuptools, site

site.ENABLE_USER_SITE = True #https://www.scivision.dev/python-pip-devel-user-install/

setupkwargs = dict(
    name='openmsipython',
    version='0.9.2.0',
    packages=setuptools.find_packages(include=['openmsipython*']),
    include_package_data=True,
    entry_points = {
        'console_scripts' : ['UploadDataFile=openmsipython.data_file_io.upload_data_file:main',
                             'DataFileUploadDirectory=openmsipython.data_file_io.data_file_upload_directory:main',
                             'DataFileDownloadDirectory=openmsipython.data_file_io.data_file_download_directory:main',
                             'InstallService=openmsipython.services.install_service:main',
                             'ManageService=openmsipython.services.manage_service:main',
                             'LecroyFileUploadDirectory=openmsipython.pdv.lecroy_file_upload_directory:main',
                             'PDVPlotMaker=openmsipython.pdv.pdv_plot_maker:main',
                             'ProvisionNode=openmsipython.utilities.provision_wrapper:main',
                             'OSNStreamProcessor=openmsipython.osn.osn_stream_processor:main',
                            ],
    },
    python_requires='>=3.7,<3.10',
    install_requires=['atomicwrites>=1.4.0',
                      'boto3>=1.23.0',
                      'confluent-kafka>=1.8.2',
                      'gemd>=1.8.1',
                      'kafkacrypto>=0.9.9.14.post1',
                      'matplotlib',
                      'methodtools',
                      'msgpack',
                      'pandas',
                      'pymssql',
                      'python-fmrest>=1.4.0',
                      'scipy; python_version>="3.8"',
                      'scipy==1.4.1; python_version=="3.7"',
                      'sqlalchemy',
                     ],
    extras_require = {'test': ['beautifulsoup4',
                               'gitpython',
                               'lxml',
                               'marko[toc]',
                               'pyflakes>=2.2.0',
                               ],
                        },
)

setupkwargs["extras_require"]["all"] = sum(setupkwargs["extras_require"].values(), [])

setuptools.setup(**setupkwargs)
