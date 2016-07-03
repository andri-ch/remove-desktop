#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

### BEGIN LICENSE
# Copyright (C) 2013 Andrei Chiver <andreichiver@gmail.com>
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

#import sys

from distutils.core import setup
import io

#setup(name='remove-desktop',
#      version='0.1',
#      py_modules=['remove_desktop'],
#      author='andri_ch',
#      author_email='andreichiver@gmail.com',
#      url='http://www.alinia.ro',
#      description='Uninstall metapackages that leave a lot of dependencies behind when removed with a package manager.',
#      )

#from distribute_setup import use_setuptools; use_setuptools()
#from setuptools import setup, find_packages


#try:
#    import DistUtilsExtra.auto    # provided by python-distutils-extra debian package
#except ImportError:
#    print >> sys.stderr, 'To build remove-desktop you need https://launchpad.net/python-distutils-extra'
#    print >> sys.stderr, 'Usually you can do that, using root user rights:'
#    print >> sys.stderr, 'sudo apt-get install python-distutils-extra'
#    sys.exit(1)
#assert DistUtilsExtra.auto.__version__ >= '2.18', 'needs DistUtilsExtra.auto >= 2.18'


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README')

#setup(
#DistUtilsExtra.auto.setup(
setup(
    name='remove-desktop',
    version='0.1',
    description='Uninstall desktops and other meta-packages ensuring that their dependencies are properly removed.',
    long_description=long_description,
    author='Andrei Chiver',
    author_email='andreichiver@gmail.com',
    license='GPLv3',
    url='http://launchpad.net/remove_desktop',
    packages=['remove_desktop'],
    package_data={'remove_desktop': ['requirements.txt']},
    # REMEMBER: python can't import pkgs that contain dash '-' in their names
    # The packages option tells the Distutils to process (build, distribute,
    # install, etc.) all pure Python modules found in each package mentioned
    # in the packages list.
    # Thus, when you say packages = ['remove-desktop'] in your setup
    # script, you are promising that the Distutils will find a file
    # remove-desktop/__init__.py
    # 'packages' can be replaced by 'package_dir'
#    scripts=['remove-desktop/remove_desktop.py',
#             'remove-desktop/utils.py',
#             'tests/test.py'],
    requires=['docopt(>=0.5.0)', 'sh(>=1.07)', 'colorlog(>=1.8)'],
    # distutils' 'requires' doesn't do anything, it's used for doc purposes.
    # Use setuptools.setup and instead of 'requires', use the key
    # 'install_requires'.
    install_requires=['docopt>=0.5.0', 'sh>=1.07', 'colorlog>=1.8'],
    # install_requires can be used by pip package manager
    provides=['remove_desktop'],
#    scripts=['scripts/remove-desktop-gui'],
    # Scripts are files containing Python source code, intended to be started from the command line.
    data_files=[('', ['remove_desktop/data/main.conf'])]
#    data_files=[('/usr/share/applications', ['hello-unity.desktop']),
#                ('/usr/share/pixmaps', ['hello-unity.svg',
#                                        'hello-unity-attention.svg',
#                                        'hello-unity-mono-dark.svg',
#                                        ]),
#                ],
)


# see an example of setup args here:
#        /usr/share/doc/python-distutils-extra/setup.py.example
