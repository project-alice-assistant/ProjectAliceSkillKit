import sys
import click

from AliceSK.validate.src.Validator import Validator
from AliceSK.util.Helpers import OptionEatAll


@click.command()
@click.option('--paths', cls=OptionEatAll, required=True, help='module paths to test')
@click.option('-v', '--verbose', count=True, help='verbosity to print')
@click.option('--token', help='github token')
def validate(paths: list, verbose: int, token: str):
	"""
	Validate Modules
	"""
	username = 'ProjectAlice'
	if not token:
		username = click.prompt('Github username')
		token = click.prompt('Github password', hide_input=True, confirmation_prompt=False)

	valid = Validator(
		modulePaths=paths,
		verbosity=verbose,
		username=username,
		token=token)
	error = valid.validate()
	sys.exit(error)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	validate()
