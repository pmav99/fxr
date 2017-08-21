#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import glob

from setuptools import setup
from setuptools import find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()


test_requirements = [
    "munch",
    "py.test",
]

setup(
    name='fxr',
    version='0.2.0',
    description="Pythonic Find and Replacetest",
    long_description=readme,
    author="Panos Mavrogiorgos",
    author_email='pmav99@gmail.com',
    url='https://github.com/pmav99/fxr',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob.glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'fxr=fxr:cli'
        ]
    },
    test_suite='tests',
    tests_require=test_requirements,

    license="MIT license",
    keywords=['find', 'replace', 'find and replace'],
    classifiers=[
        'Development Status :: 2 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
