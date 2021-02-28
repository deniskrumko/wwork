#!/usr/bin/env python3

from setuptools import setup

from wwork import get_version

with open('README.rst') as f:
    readme = f.read()

setup(
    name='wwork',
    version=get_version(),
    description='CLI for time management',
    long_description=readme,
    author='Denis Krumko',
    author_email='dkrumko@gmail.com',
    url='https://github.com/deniskrumko/wwork',
    license="MIT",
    entry_points={
        'console_scripts': [
            'ww = wwork.main:main',
        ],
    },
    packages=['wwork'],
    python_requires=">=3.7",
    keywords='CLI, Jira, Time management',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
