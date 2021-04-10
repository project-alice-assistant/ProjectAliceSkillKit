import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator

from jsonschema import Draft7Validator, exceptions


class Validation(ABC):

	def __init__(self):
		self._skillPath = None
		self._dirPath = Path(__file__).resolve().parent
		self._basePath = self._dirPath.parent.parent.parent
		self._error = False
		self._warning = False
		self._files = dict()
		self.errors = ''
		self.warnings = ''


	def reset(self, skillPath: Path):
		self._skillPath = skillPath
		self._error = False
		self._warning = False
		self.errors = ''
		self.warnings = ''


	@property
	def errorCode(self) -> bool:
		return self._error


	@property
	def warning(self) -> bool:
		return self._warning


	def saveIndentedError(self, indent: int, *args):
		self.errors += ' ' * indent + ' '.join(map(str, args)) + '\n'


	def saveIndentedWarning(self, indent: int, *args):
		self.warnings += ' ' * indent + ' '.join(map(str, args)) + '\n'


	@property
	@abstractmethod
	def jsonSchema(self) -> dict:
		pass


	@property
	@abstractmethod
	def jsonFiles(self) -> Generator[Path, None, None]:
		pass


	def validateSyntax(self, file: Path) -> dict:
		data: dict = dict()
		try:
			data = json.loads(file.read_text(encoding='utf-8'))
		except FileNotFoundError:
			self.saveIndentedError(2, f'Required file {file.parent.name}/{file.name} not found')
			self._error = True
		except Exception as e:
			self.saveIndentedError(2, f'Syntax errors in {file.parent.name}/{file.name}:')
			self.saveIndentedError(4, f'- {e}')
			self._error = True

		return data


	def printErrorList(self, errorList: list, indent: int = 0):
		if errorList:
			for error in errorList:
				self.saveIndentedError(indent, '-', error)
			self.saveIndentedError(0)


	def printWarningList(self, warningList: list, indent: int = 0):
		if warningList:
			for warning in warningList:
				self.saveIndentedWarning(indent, '-', warning)
			self.saveIndentedWarning(0)


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
			self.saveIndentedError(2, f'Schema errors in {file.parent.name}/{file.name}:')
			self.printErrorList(errors, 4)


	def validateJsonSchemas(self):
		for file in self.jsonFiles:
			self.validateJsonSchema(file)


	@abstractmethod
	def validate(self, verbosity: int = 0) -> bool:
		pass
