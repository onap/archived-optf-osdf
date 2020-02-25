# -*- encoding: utf-8 -*-
# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

'''Setup'''

import setuptools

setuptools.setup(name='of-osdf',
      version='1.0',
      description='Python Distribution Utilities',
      author='xyz',
      author_email='xyz@wipro.com',
      url='https://wiki.onap.org/display/DW/Optimization+Service+Design+Framework',
      classifiers=[
		  'Development Status :: 4 - Beta',
		  'Environment :: ONAP',
		  'Intended Audience :: Information Technology',
		  'Intended Audience :: System Administrators',
		  'License :: OSI Approved :: Apache Software License',
		  'Operating System :: POSIX :: Linux',
		  'Programming Language :: Python',
		  'Programming Language :: Python :: 3'
		  'Programming Language :: Python :: 3.5'
		  'Topic :: Communications :: Email',
		  'Topic :: Office/Business',
		  'Topic :: Software Development :: Bug Tracking',],
      keywords=['onap','osdf'],
      packages=['osdf'],
      entry_points = {
        'console_scripts': [
            'cipher-utility = osdf.cmd.encryptionUtil:main',
        ],
      'oslo.config.opts': [
    	'osdf = osdf.opts:list_opts',
      ],
      }
     )
