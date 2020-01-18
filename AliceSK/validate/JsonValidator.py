import sys
import click

from AliceSK.validate.src.Validator import Validator
from AliceSK.util.Helpers import OptionEatAll


@click.command()
@click.option('--paths', cls=OptionEatAll, required=True, help='skill paths to test')
@click.option('-v', '--verbose', count=True, help='verbosity to print')
def validate(paths: list, verbose: int):
	"""
	Validate Skills
	"""

	valid = Validator(
		skillPaths=paths,
		verbosity=verbose)
	error = valid.validate()
	sys.exit(error)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
