#imports
import setuptools, site

site.ENABLE_USER_SITE = True #https://www.scivision.dev/python-pip-devel-user-install/

setupkwargs = dict(
    name='openmsipython',
    version='0.9.4.1',
    packages=setuptools.find_packages(include=['openmsipython*']),
    include_package_data=True,
    entry_points = {
        'console_scripts' : ['LecroyFileUploadDirectory=openmsipython.pdv.lecroy_file_upload_directory:main',
                             'PDVPlotMaker=openmsipython.pdv.pdv_plot_maker:main',
                            ],
    },
    python_requires='>=3.7,<3.10',
    install_requires=['gemd>=1.9.0',
                      'matplotlib',
                      'methodtools',
                      'openmsistream>=0.9.1.4',
                      'pandas',
                      'python-fmrest>=1.4.0',
                      'scipy; python_version>="3.8"',
                      'scipy==1.4.1; python_version=="3.7"',
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
