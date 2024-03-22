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

 Direct install for all systems:
   "python setup.py install"
"""


from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

from setuptools import setup

setup(
      name='GSOF_ArduBridge',
      version='0.1',
      description='Protocol stack for bridge between the Arduino and Python',
      long_description=readme(),
      classifiers=[
        'Development Status ::  Production/Stable',
        'License :: GPL-3.0-or-later',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Communications and control:: ',
      ],
      platforms = 'any',
      keywords='ArduBridge',
      url = 'https://github.com/mrGSOF/arduBridge.git',
      author='Guy Soffer',
      author_email='gsoffer@yahoo.com',
      license='GPL-3.0-or-later',
      packages=['GSOF_ArduBridge'],
      install_requires=[
        'pyserial>=2.7',
    ]
)
