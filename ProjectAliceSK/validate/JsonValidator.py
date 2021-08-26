#  Copyright (c) 2021
#
#  This file, JsonValidator.py, is part of Project Alice.
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
import sys
from pathlib import Path
from typing import Union


try:
	from ProjectAliceSK.util.Helpers import OptionEatAll
	from ProjectAliceSK.validate.src.Validator import Validator
except ModuleNotFoundError:
	from util.Helpers import OptionEatAll
	from validate.src.Validator import Validator


@click.command()
@click.option('-p', '--paths', default=None, cls=OptionEatAll, help='Paths to test')
@click.option('-v', '--verbose', count=True, help='Verbosity level')
def validate(paths: Union[str, list], verbose: int):
	"""
	Validates skills
	"""
	if not paths:
		paths = [os.getcwd()]

	try:
		test = Path(paths[0])
		if test.is_dir():
			if Path(test / 'dialogTemplate').exists():
				raise Exception

			paths = tuple([str(d) for d in test.iterdir() if d.is_dir()])
	except:
		pass  # do nothing

	validator = Validator(skillPaths=paths, verbosity=verbose)
	error = validator.validate()
	sys.exit(error)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
