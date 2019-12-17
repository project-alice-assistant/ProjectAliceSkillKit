import sys
import click

from AliceSK.validate.src.Validator import Validator
from AliceSK.util.Helpers import OptionEatAll


@click.command()
@click.option('--paths', cls=OptionEatAll, required=True, help='skill paths to test')
@click.option('-v', '--verbose', count=True, help='verbosity to print')
@click.option('--token', help='github token')
@click.option('--branch', help='branch to take core skills from')
def validate(paths: list, verbose: int, token: str, branch: str):
	"""
	Validate Skills
	"""

	valid = Validator(
		skillPaths=paths,
		branch=branch or 'master',
		verbosity=verbose,
		username='ProjectAlice',
		token=token)
	error = valid.validate()
	sys.exit(error)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
