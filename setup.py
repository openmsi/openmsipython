#imports
import setuptools

setupkwargs = dict(
    name='openmsipython',
    version='0.9.5',
    packages=setuptools.find_packages(include=['openmsipython*']),
    include_package_data=True,
    entry_points = {
        'console_scripts' : ['LecroyFileUploadDirectory=openmsipython.pdv.lecroy_file_upload_directory:main',
                             'PDVPlotMaker=openmsipython.pdv.pdv_plot_maker:main',
                            ],
    },
    python_requires='>=3.7,<3.10',
    install_requires=['gemd>=1.10.2',
                      'matplotlib',
                      'methodtools',
                      'openmsistream>=1.5.1',
                      'pandas',
                      'python-fmrest>=1.6.0',
                      'scipy; python_version>="3.8"',
                      'scipy==1.4.1; python_version=="3.7"',
                     ],
    extras_require = {'test': ['beautifulsoup4',
                               'gitpython',
                               'lxml',
                               'marko[toc]',
                               'pyflakes>=2.5.0',
                               ],
                        },
)

setupkwargs["extras_require"]["all"] = sum(setupkwargs["extras_require"].values(), [])

setuptools.setup(**setupkwargs)
