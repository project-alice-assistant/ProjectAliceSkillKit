from pathlib import Path

import click

from ProjectAliceSK.validate.src.ConfigValidation import ConfigValidation
from ProjectAliceSK.validate.src.DialogValidation import DialogValidation
from ProjectAliceSK.validate.src.InstallValidation import InstallValidation
from ProjectAliceSK.validate.src.TalkValidation import TalkValidation
from ProjectAliceSK.validate.src.Validation import Validation


class Validator:

	def __init__(self, skillPaths: list, verbosity: int):
		self._dirPath = Path(__file__).resolve().parent.parent
		self._skillPath = self._dirPath.parent.parent
		self._skillPaths = skillPaths
		self._verbosity = verbosity


	@staticmethod
	def indentPrint(indent: int, *args):
		click.echo(' ' * (indent - 1) + ' '.join(map(str, args)))


	def validate(self):
		err = 0
		dialog = DialogValidation()
		installer = InstallValidation()
		talk = TalkValidation()
		config = ConfigValidation()

		for skillPath in self._skillPaths:
			skill = Path(skillPath).resolve()
			if not skill.is_dir():
				self.indentPrint(0, click.style(f'The path {skillPath} is invalid', fg='red', bold=True))
				continue

			dialog.reset(skill)
			installer.reset(skill)
			talk.reset(skill)
			config.reset(skill)

			dialog.validate(self._verbosity)
			installer.validate()
			talk.validate()
			config.validate()

			if dialog.errorCode or installer.errorCode or talk.errorCode:
				err = 1
				self.indentPrint(0, click.style(f'{skill.name}', fg='red', bold=True), 'invalid')
				self.printErrors('Installer', installer)
				self.printErrors('Dialog files', dialog)
				self.printErrors('Talk files', talk)
				self.printErrors('Config file', config)
				self.indentPrint(0)
			else:
				self.indentPrint(0, click.style(f'{skill.name}', fg='green', bold=True), 'valid')

		return err


	def printErrors(self, name: str, validation: Validation):
		if validation.errorCode:
			self.indentPrint(2, click.style(f'{name}:', bold=True))
			click.echo(validation.errors)
		else:
			self.indentPrint(2, click.style(name, bold=True), 'valid')
