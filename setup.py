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
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
      name='GSOF_ArduBridge',
      version='0.13',
      description='Protocol stack to bridge between an Arduino and Python',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
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
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Embedded Systems',
      ],
      platforms = 'any',
      keywords='ArduBridge',
      url = 'https://github.com/mrGSOF/arduBridge.git',
      author='Guy Soffer',
      author_email='gsoffer@yahoo.com',
      license='GPL-3.0-or-later',
      packages=['GSOF_ArduBridge', 'GSOF_ArduBridge.device'],
      install_requires=[
        'pyserial>=2.7',
    ]
)
