import os
import sys

import click

from ProjectAliceSK.util.Helpers import OptionEatAll
from ProjectAliceSK.validate.src.Validator import Validator


@click.command()
@click.option('-p', '--paths', 'string', cls=OptionEatAll, required=False, help='Paths to test')
@click.option('-v', '--verbose', count=True, help='Verbosity level')
def validate(paths: list, verbose: int):
	"""
	Validate Skills
	"""

	if not paths:
		paths = [os.getcwd()]

	valid = Validator(
		skillPaths=paths,
		verbosity=verbose)
	error = valid.validate()
	sys.exit(error)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
