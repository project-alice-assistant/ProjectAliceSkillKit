import json
from pathlib import Path
from typing import Generator

from jsonschema import Draft7Validator, exceptions

from ProjectAliceSK.validate.src.Validation import Validation


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
