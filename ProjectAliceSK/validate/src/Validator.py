#  Copyright (c) 2021
#
#  This file, Validator.py, is part of Project Alice.
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
from pathlib import Path


try:
	from ProjectAliceSK.validate.src.ConfigValidation import ConfigValidation
	from ProjectAliceSK.validate.src.DialogValidation import DialogValidation
	from ProjectAliceSK.validate.src.InstallValidation import InstallValidation
	from ProjectAliceSK.validate.src.TalkValidation import TalkValidation
	from ProjectAliceSK.validate.src.Validation import Validation
	from ProjectAliceSK.validate.src.SamplesValidation import SamplesValidation
except ModuleNotFoundError:
	from validate.src.ConfigValidation import ConfigValidation
	from validate.src.DialogValidation import DialogValidation
	from validate.src.InstallValidation import InstallValidation
	from validate.src.TalkValidation import TalkValidation
	from validate.src.Validation import Validation
	from validate.src.SamplesValidation import SamplesValidation


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
		samples = SamplesValidation()

		for skillPath in self._skillPaths:
			skill = Path(skillPath).resolve()
			if not skill.is_dir():
				self.indentPrint(0, click.style(f'The path {skillPath} is invalid', fg='red', bold=True))
				continue

			dialog.reset(skill)
			installer.reset(skill)
			talk.reset(skill)
			config.reset(skill)
			samples.reset(skill)

			dialog.validate(self._verbosity)
			installer.validate()
			talk.validate()
			config.validate()
			samples.validate()

			if dialog.errorCode or installer.errorCode or talk.errorCode or samples.errorCode:
				err = 1
				self.indentPrint(0, click.style(f'{skill.name}', fg='red', bold=True), 'invalid')
				self.printErrors('Installer', installer)
				self.printErrors('Dialog files', dialog)
				self.printErrors('Talk files', talk)
				self.printErrors('Config file', config)
				self.printErrors('Sample files', samples)
				self.indentPrint(0)
			elif dialog.warning or installer.warning or talk.warning or samples.warning:
				self.indentPrint(0, click.style(f'{skill.name}', fg='yellow', bold=True), 'warning')
				self.printWarnings('Installer', installer)
				self.printWarnings('Dialog files', dialog)
				self.printWarnings('Talk files', talk)
				self.printWarnings('Config file', config)
				self.printWarnings('Sample files', samples)
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


	def printWarnings(self, name: str, validation: Validation):
		if validation.warning:
			self.indentPrint(2, click.style(f'{name}:', bold=True))
			click.echo(validation.warnings)
		else:
			self.indentPrint(2, click.style(name, bold=True), 'valid')
