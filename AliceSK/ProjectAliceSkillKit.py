import click
import importlib.util
from pathlib import Path

from AliceSK.validate.JsonValidator import validate
from AliceSK.create.create import create

@click.group(context_settings={'help_option_names':['--help', '-h']})
def cli():
		"""
		This is the Command Line Interface of the Project Alice Skill Kit.
		Currently the following commands are supported.
		"""
		pass

cli.add_command(validate)
cli.add_command(create)


if __name__ == '__main__':
	cli()

