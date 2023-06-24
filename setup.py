"""
 setup.py for GSOF Arduino Bridge Protocol Stack

    This file is part of GSOF_ArduBridge.

    GSOF_ArduBridge is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GSOF_ArduBridge is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GSOF_ArduBridge.  If not, see <https://www.gnu.org/licenses/>.

 Under windows install:
   "setup.bat"

 Direct install (all systems):
   "python setup.py install"
"""

from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
      name='Ardu-BridgeStack',
      version='0.1',
      description='Protocol stack for bridge between the Arduino and Python',
      long_description=readme(),
      classifiers=[
        'Development Status ::  Production',
        'License :: GPL-3.0-or-later',
        'Programming Language :: Python :: 2.7 and Python 3',
        'Topic :: Communications and control:: ',
      ],
      platforms = 'any',
      keywords='ArduBridge',
      url='None',
      author='Guy Soffer',
      author_email='gsoffer@yahoo.com',
      license='GPL-3.0-or-later',
      packages=['GSOF_ArduBridge'],
)
