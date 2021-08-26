#  Copyright (c) 2021
#
#  This file, TalkValidation.py, is part of Project Alice.
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

import json
from pathlib import Path
from typing import Generator


try:
	from ProjectAliceSK.validate.src.Validation import Validation
except ModuleNotFoundError:
	from validate.src.Validation import Validation


class TalkValidation(Validation):

	@property
	def jsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/talk-schema.json'
		return json.loads(schema.read_text(encoding='utf-8'))


	@property
	def jsonFiles(self) -> Generator[Path, None, None]:
		return self._skillPath.glob('talks/*.json')


	def validateTypes(self):
		# check whether the same slots appear in all files
		for file in self.jsonFiles:
			warnings = [talkType for talkType in self._files['en'] if talkType not in self._files[file.stem]]
			if warnings:
				self.saveIndentedWarning(2, f'Missing translations in {file.parent.name}/{file.name}:')
				self.printWarningList(warnings, 4)
				self._warning = True


	def loadFiles(self):
		for file in self.jsonFiles:
			data = self.validateSyntax(file)
			self._files[file.stem] = data


	def validate(self, verbosity: int = 0) -> bool:
		self.loadFiles()
		if self._files['en']:
			self.validateJsonSchemas()
			self.validateTypes()
		return self._error
