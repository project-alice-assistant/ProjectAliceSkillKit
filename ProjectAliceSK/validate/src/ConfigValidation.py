#  Copyright (c) 2021
#
#  This file, ConfigValidation.py, is part of Project Alice.
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
from typing import Generator, Optional


try:
	from ProjectAliceSK.validate.src.Validation import Validation
except ModuleNotFoundError:
	from validate.src.Validation import Validation

class ConfigValidation(Validation):

	@property
	def jsonFiles(self) -> Generator[Path, None, None]:
		return self._skillPath.glob('config.json.template')


	@property
	def jsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/config-schema.json'
		return json.loads(schema.read_text(encoding='utf-8'))


	@property
	def configFile(self) -> Optional[Path]:
		filePath = self._skillPath / 'config.json.template'
		return filePath if filePath.exists() else None


	def validate(self, verbosity: int = 0) -> bool:
		configFile = self.configFile
		if not configFile:
			return True

		self.validateSyntax(configFile)
		self.validateJsonSchema(configFile)
		return self._error
