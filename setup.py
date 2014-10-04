#!/usr/bin/env python
import os
import setuptools
import sys

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setuptools.setup(
        name='fzsl',
        version='1.0',
        description='Fuzzy path searching for shells',
        long_description=(read('README.txt')),
        author='Justin Bronder',
        author_email='jsbronder@gmail.com',
        url='http://github.com/jsbronder/fzsl',
        include_package_data=True,
        keywords='fuzzy shell search',
        packages=['fzsl'],
        data_files=[
            ('%s/etc/fzsl' % (sys.prefix,), ['etc/fzsl.bash', 'etc/fzsl.conf']),
        ],
        scripts=['bin/fzsl'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Python Modules',],
)
