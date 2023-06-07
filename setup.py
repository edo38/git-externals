#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import warnings
from zipfile import ZipFile
from distutils import dir_util

try:
    from setuptools import setup
    from setuptools.command.bdist_egg import bdist_egg
except ImportError:
    from distutils.core import setup


with open('git_externals/__init__.py') as fp:
    exec(fp.read())


classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

class BDistEgg(bdist_egg):
    """ custom egg builder """
    def finalize_options(self):
        self.exclude_source_files = True
        build_cmd = self.get_finalized_command('build')
        build_base = build_cmd.build_base
        self.reinitialize_command(build_cmd, reinit_subcommands=1)
        if os.path.exists(build_base):
            dir_util.remove_tree(build_base, dry_run=self.distribution.dry_run)
        self.distribution.command_options['easy_install'] = {'editable':('setup.py',True),
            'always_copy':('setup.py',True),
            'verbose':('setup.py',0),
            'build_directory':('setup.py',build_base),
            'args':('setup.py',['click==6.7','git_svn_clone_externals==1.1.6'])
        }
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            ei_cmd = self.distribution.get_command_obj('easy_install', create=1)
            ei_cmd.ensure_finalized()
            self.run_command('easy_install')
        del self.distribution.command_options['easy_install']
        self.distribution.packages.append('click')
        self.distribution.package_dir['click'] = os.path.join(build_base,
            'click','click')
        self.distribution.py_modules.append('git_svn_clone_externals')
        self.distribution.package_dir[''] = os.path.join(build_base,
            'git-svn-clone-externals')
        self.distribution.entry_points['setuptools.installation'] = [
            'eggsecutable = git_externals.cli:cli',
        ]
        bdist_egg.finalize_options(self)

    def run(self):
        bdist_egg.run(self)
        with ZipFile(self.egg_output, mode='a') as eggz:
            eggz.writestr('__main__.py','''\
# -*- coding: utf-8 -*-
import git_externals.cli
git_externals.cli.cli()
''')

setup(
    name='git-externals',
    version=__version__,
    description='cli tool to manage git externals',
    long_description='Ease the migration from Git to SVN by handling svn externals through a cli tool',
    packages=['git_externals'],
    package_dir={'git_externals':'git_externals'},
    py_modules=[],
    install_requires=['click',
                      'git-svn-clone-externals'],
    entry_points={
        'console_scripts': [
            'git-externals = git_externals.cli:cli',
            'svn-externals-info = git_externals.process_externals:main',
        ],
    },
    cmdclass={
        'bdist_egg':BDistEgg
    },
    author=__author__,
    author_email=__email__,
    license='MIT',
    classifiers=classifiers,
)
