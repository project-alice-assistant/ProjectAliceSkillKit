import json
from pathlib import Path
from typing import Generator, Optional

from ProjectAliceSK.validate.src.Validation import Validation


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
