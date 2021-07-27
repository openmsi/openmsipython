#imports
import setuptools, site

site.ENABLE_USER_SITE = True #https://www.scivision.dev/python-pip-devel-user-install/

setupkwargs = dict(
    name='openmsipython',
    version='0.0.2',
    packages=setuptools.find_packages(include=['openmsipython*']),
    include_package_data=True,
    entry_points = {
        'console_scripts' : ['upload_data_file=openmsipython.data_file_io.upload_data_file:main',
                             'data_file_upload_directory=openmsipython.data_file_io.data_file_upload_directory:main',
                             'data_file_download_directory=openmsipython.data_file_io.data_file_download_directory:main',
                             'manage_service=openmsipython.services.manage_service:main',
                             'lecroy_file_upload_directory=openmsipython.pdv.lecroy_file_upload_directory:main',
                             'pdv_plot_maker=openmsipython.pdv.pdv_plot_maker:main',
                            ],
    },
    python_requires='>=3.7,<3.8',
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