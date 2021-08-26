#  Copyright (c) 2021
#
#  This file, InstallValidation.py, is part of Project Alice.
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

import json
from jsonschema import Draft7Validator, exceptions
from pathlib import Path
from typing import Generator


try:
	from ProjectAliceSK.validate.src.Validation import Validation
except ModuleNotFoundError:
	from validate.src.Validation import Validation


class InstallValidation(Validation):

	@property
	def jsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/install-schema.json'
		return json.loads(schema.read_text(encoding='utf-8'))


	@property
	def jsonFiles(self) -> Generator[Path, None, None]:
		return self._skillPath.glob('*.install')


	def validateJsonSchema(self, file: Path):
		schema = self.jsonSchema
		data = self.validateSyntax(file)
		errors = list()
		try:
			Draft7Validator(schema).validate(data)
		except exceptions.ValidationError:
			self._error = True
			for error in sorted(Draft7Validator(schema).iter_errors(data), key=str):
				errors.append(error.message)

		if errors:
			self.saveIndentedError(2, f'schema errors in {file.name}:')
			self.printErrorList(errors, 4)


	def validate(self, verbosity: int = 0) -> bool:
		self.validateJsonSchemas()
		return self._error
