import click

try:
	from ProjectAliceSK.create.create import create
	from ProjectAliceSK.makeTalks.makeTalks import makeTalks
	from ProjectAliceSK.validate.JsonValidator import validate
except ModuleNotFoundError:
	from create.create import create
	from makeTalks.makeTalks import makeTalks
	from validate.JsonValidator import validate


@click.group(context_settings={'help_option_names': ['--help', '-h']})
def cli():
	"""
	This is the Command Line Interface of the Project Alice Skill Kit.
	Currently the following commands are supported.
	"""
	pass


cli.add_command(validate)
cli.add_command(create)
cli.add_command(makeTalks)

if __name__ == '__main__':
	cli()
