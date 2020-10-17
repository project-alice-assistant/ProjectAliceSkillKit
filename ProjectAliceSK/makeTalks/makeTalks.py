import os
from pathlib import Path
import click

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
