#  Copyright (c) 2021
#
#  This file, setup.py, is part of Project Alice.
#
#  Project Alice is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#  Last modified: 2021.07.28 at 16:35:13 CEST

import io

from setuptools import find_packages, setup


with io.open('README.md', 'rt', encoding="utf8") as f:
	readme = f.read()

setup(
	name='projectalice-sk',
	author='ProjectAlice',
	version='2.3.4',
	maintainer='Psychokiller1888',
	maintainer_email='laurentchervet@bluewin.ch',
	description='Project Alice skill kit',
	long_description=readme,
	long_description_content_type='text/markdown',
	url='https://github.com/project-alice-assistant/ProjectAliceSkillKit',
	license='GPL-3.0',
	packages=find_packages(),
	include_package_data=True,
	use_scm_version=False,
	setup_requires=['setuptools_scm'],
	install_requires=[
		'AliceGit',
		'jsonschema>=3.0.0',
		'click',
		'unidecode',
		'requests',
		'InquirerPy~=0.3.1',
		'jinja2',
		'pytest~=6.2.5',
		'coverage~=6.2',
		'pytest-cov~=3.0.0',
		'coveralls~=3.3.1',
		'types-requests'
	],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3.7",
		"Topic :: Software Development :: Code Generators",
		"Topic :: Software Development :: Testing"
	],
    entry_points='''
        [console_scripts]
        projectalice-sk=ProjectAliceSK.ProjectAliceSkillKit:cli
        aliceSk=ProjectAliceSK.ProjectAliceSkillKit:cli
    '''
)
