import os
import sys
from pathlib import Path
from typing import Union

import click

from ProjectAliceSK.util.Helpers import OptionEatAll
from ProjectAliceSK.validate.src.Validator import Validator


@click.command()
@click.option('-p', '--paths', default=None, cls=OptionEatAll, help='Paths to test')
@click.option('-v', '--verbose', count=True, help='Verbosity level')
def validate(paths: Union[str, list], verbose: int):
	"""
	Validate Skills
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
