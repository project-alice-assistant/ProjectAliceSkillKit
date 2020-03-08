import sys

import click
import os

from ProjectAliceSK.util.Helpers import OptionEatAll
from ProjectAliceSK.validate.src.Validator import Validator


@click.command()
@click.option('-p', '--paths', default=None, cls=OptionEatAll, help='Paths to test')
@click.option('-v', '--verbose', count=True, help='Verbosity level')
def validate(paths: list, verbose: int):
	"""
	Validate Skills
	"""

	if not paths:
		paths = [os.getcwd()]

	validator = Validator(skillPaths=paths, verbosity=verbose)
	error = validator.validate()
	sys.exit(error)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
