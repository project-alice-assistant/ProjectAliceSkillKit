#  Copyright (c) 2021
#
#  This file, unittests.py, is part of Project Alice.
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
#  Last modified: 2021.07.28 at 16:35:11 CEST

import click
import os
import pytest
import sys
from pathlib import Path


@click.command()
@click.option('-s', '--skill', default=None, type=str, help='The skill to run tests on')
def unittests(skill: str):
	if not skill:
		skill = os.getcwd()

	skillPath = Path(skill)
	path = skillPath / 'tests'
	if not path.exists():
		print('No unittests found, aborting')
		sys.exit(0)

	print('Found tests to be run, starting')
	result = pytest.main([str(path), '--cov=./', '--cov-report=xml'])
	if isinstance(result, int):
		ret = 0 if result == 5 else result
	else:
		ret = 0 if result.value == 5 else result.value
	sys.exit(ret)


if __name__ == '__main__':
	unittests()
