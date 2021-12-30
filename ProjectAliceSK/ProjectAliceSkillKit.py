#  Copyright (c) 2021
#
#  This file, ProjectAliceSkillKit.py, is part of Project Alice.
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
#  Last modified: 2021.07.28 at 16:35:13 CEST

import click


try:
	from ProjectAliceSK.create.create import create
	from ProjectAliceSK.create.create import createWidget
	from ProjectAliceSK.create.create import createDeviceType
	from ProjectAliceSK.create.create import createNode
	from ProjectAliceSK.create.create import uploadToGithub
	from ProjectAliceSK.makeTalks.makeTalks import makeTalks
	from ProjectAliceSK.validate.JsonValidator import validate
	from ProjectAliceSK.unittests.unittests import unittests
except ModuleNotFoundError:
	from create.create import create
	from create.create import createWidget
	from create.create import createDeviceType
	from create.create import createNode
	from makeTalks.makeTalks import makeTalks
	from validate.JsonValidator import validate
	from unittests.unittests import unittests


@click.group(context_settings={'help_option_names': ['--help', '-h']})
def cli():
	"""
	This is the Command Line Interface of the Project Alice Skill Kit.
	Currently the following commands are supported.
	"""
	pass


cli.add_command(validate)
cli.add_command(create)
cli.add_command(createWidget)
cli.add_command(createDeviceType)
cli.add_command(createNode)
cli.add_command(uploadToGithub)
cli.add_command(makeTalks)
cli.add_command(unittests)

if __name__ == '__main__':
	cli()
