#!/usr/bin/env python

import distutils.core

distutils.core.setup(
        name='fzsl',
        version='1.0',
        description='Fuzzy path searching for shells',
        author='Justin Bronder',
        author_email='jsbronder@gmail.com',
        url='http://github.com/jsbronder/fzsl',
        packages=['fzsl'],
        scripts=['bin/fzsl'],
        data_files=[
            ('/etc/fzsl', ['fzsl.bash', 'etc/fzsl.conf']),
        ],
        license='BSD',
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
