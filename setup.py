#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

# with open('HISTORY.rst') as history_file:
    # history = history_file.read()

requirements = [
    # 'Click>=6.0',
    # TODO: put package requirements here
]

test_requirements = [
    'munch',
    # TODO: put package test requirements here
]

setup(
    name='fxr',
    version='0.1.0',
    description="Pythonic Find and Replacetest",
    long_description=readme,
    author="Panos Mavrogiorgos",
    author_email='pmav99@gmail.com',
    url='https://github.com/pmav99/fxr',
    packages=[
        'fxr',
    ],
    package_dir={'fxr': 'fxr'},
    entry_points={
        'console_scripts': [
            'fxr=fxr:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
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
    test_suite='tests',
    tests_require=test_requirements
)
