#!/usr/bin/env python3

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='wwork',
    version='0.0.1',
    description='CLI for managing work logs with JIRA integration',
    long_description=readme,
    author='Timothy Crosley',
    author_email='timothy.crosley@gmail.com',
    url='https://github.com/deniskrumko/wwork',
    license="MIT",
    entry_points={
        'console_scripts': [
            'wwork = wwork.main:main',
        ],
    },
    packages=['wwork'],
    python_requires=">=3.6",
    keywords='Time management, Logging, Work, JIRA',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
