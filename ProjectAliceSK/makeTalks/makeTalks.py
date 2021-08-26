#  Copyright (c) 2021
#
#  This file, makeTalks.py, is part of Project Alice.
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
from pathlib import Path


try:
	from ProjectAliceSK.makeTalks import TalkCreator
except:
	from makeTalks import TalkCreator


@click.command()
@click.option('-s', '--skill', required=True, help='The skill name to work on', type=str, prompt='For what skill name?')
@click.option('-l', '--lang', default='all', help='Lang code to generate languages for', type=click.Choice(['all', 'en', 'de', 'fr', 'it'], case_sensitive=False), prompt='For what language? (all, en, de, fr, it)')
def makeTalks(skill: str, lang: str):
	"""
	Generates talks files based on hardcoded values in skills
	"""

	skillPath = Path(os.getcwd())
	while not Path(skillPath, skill).exists():
		path = click.prompt('Skill not found, please input the directory where its folder is located')
		skillPath = Path(path)

	skillPath = skillPath / skill

	copy2talk = TalkCreator.CopyTooTalk()
	copy2talk.checkForLogInfo(skill=skillPath, language=lang)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	makeTalks()
