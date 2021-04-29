#imports
import setuptools, site

site.ENABLE_USER_SITE = True #https://www.scivision.dev/python-pip-devel-user-install/

setuptools.setup(
    name="dmrefpython",
    version="0.0.1",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=['confluent-kafka>=1.6.0',
                      'msgpack>=1.0.0',
                     ],
    extras_require={
        'windows_services':['pywin32',],
    }
)