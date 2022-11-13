import os
import re
import sys
from setuptools import find_packages, setup

install_requires = []


if __name__ == '__main__':

    setup(
        name='superinsight-db-server',
        version='0.0.9',
        description='Superinsight DB Server',
        packages=find_packages(exclude=('tests', 'tests.*')),
        install_requires=install_requires,
        zip_safe=False,
        classifiers=[
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Testing',
        ]
    )
