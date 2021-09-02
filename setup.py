#imports
import setuptools, site

site.ENABLE_USER_SITE = True #https://www.scivision.dev/python-pip-devel-user-install/

setupkwargs = dict(
    name='openmsipython',
    version='0.1.0',
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
                            ],
    },
    python_requires='>=3.7',
    install_requires=['confluent-kafka>=1.6.0',
                      'msgpack>=1.0.0',
                      'pandas>=1.3.0',
                      'matplotlib>=3.4.0',
                      'scipy>=1.7.0',
                     ],
    extras_require = {'test': ['pyflakes>=2.2.0',],},
)

setupkwargs["extras_require"]["all"] = sum(setupkwargs["extras_require"].values(), [])

setuptools.setup(**setupkwargs)