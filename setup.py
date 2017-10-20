#!/usr/bin/env python

VERSION = '0.4'
PACKAGE = 'fzsl'

import setuptools

setuptools.setup(
        name=PACKAGE,
        version='0.4',
        description='Fuzzy path searching for shells',
        license='BSD',
        long_description=open('README.rst').read(),
        author='Justin Bronder',
        author_email='jsbronder@cold-front.org',
        url='http://github.com/jsbronder/%s' % (PACKAGE,),
        keywords='fuzzy shell search console match ncurses',
        packages=[PACKAGE],
        package_data = {
          '': ['*.rst', 'etc/fzsl.*', 'LICENSE'],
        },
        data_files = [
          ('share/fzsl/', ['README.rst', 'LICENSE', 'etc/fzsl.bash', 'etc/fzsl.conf']),
        ],
        scripts=['bin/fzsl'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Console :: Curses',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: System :: Shells',
            'Topic :: System :: Systems Administration',
            'Topic :: System :: System Shells',
            'Topic :: Terminals',
            'Topic :: Terminals :: Serial',
            'Topic :: Terminals :: Telnet',
            'Topic :: Terminals :: Terminal Emulators/X Terminals',
            'Topic :: Text Processing :: Filters',
            'Topic :: Utilities',
        ]
)
