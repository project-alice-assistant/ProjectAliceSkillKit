import json
from pathlib import Path
from typing import Generator, Optional, Tuple, Union
from unidecode import unidecode
import requests
from functools import lru_cache

from AliceSK.validate.src.DialogTemplate import DialogTemplate
from AliceSK.validate.src.Validation import Validation


class DialogValidation(Validation):

	@lru_cache()
	def getCoreSkills(self) -> dict:
		try:
			url = f'https://api.github.com/repositories/193512918/contents/PublishedSkills/ProjectAlice?ref={self._branch}'
			skillsRequest = requests.get(url, auth=self._githubAuth)
			skillsRequest.raise_for_status()
			return skillsRequest.json()
		#TODO maybe print error to console when auth failed
		except requests.RequestException:
			return dict()


	@lru_cache()
	def getCoreSkillTemplates(self, language: str) -> list:
		dialogTemplates = list()
		for skill in self.getCoreSkills():
			try:
				skillName = skill['name']
				url = f'https://raw.githubusercontent.com/project-alice-assistant/ProjectAliceSkills/{self._branch}/PublishedSkills/ProjectAlice/{skillName}/dialogTemplate/{language}.json'
				skillRequest = requests.get(url)
				skillRequest.raise_for_status()
				dialogTemplates.append(skillRequest.json())
			except (requests.RequestException, KeyError):
				continue
		return dialogTemplates


	@property
	def jsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/dialog-schema.json'
		return json.loads(schema.read_text())


	@property
	def jsonFiles(self) -> Generator[Path, None, None]:
		return self._skillPath.glob('dialogTemplate/*.json')


	@staticmethod
	def isSnipsBuiltinSlot(slot: str) -> bool:
		# check whether the slot is a integrated one from snips
		# hardcode supported slot types, since install snips_nlu_parsers
		# requires a rust compiler, which is a lot of overhead for the
		# few slot types
		snipsSlots = {
			'snips/date',
			'snips/timePeriod',
			'snips/datePeriod',
			'snips/amountOfMoney',
			'snips/time',
			'snips/musicArtist',
			'snips/musicTrack',
			'snips/region',
			'snips/musicAlbum',
			'snips/country',
			'snips/number',
			'snips/percentage',
			'snips/datetime',
			'snips/city',
			'snips/duration',
			'snips/temperature',
			'snips/ordinal'}

		return slot in snipsSlots


	@staticmethod
	def installerJsonFiles(skillPath: Path) -> Generator[Path, None, None]:
		return skillPath.glob('*.install')


	def getRequiredSkills(self, skillPath: Path = None) -> set:
		skillPath = Path(skillPath) if skillPath else self._skillPath
		skills = {skillPath}
		# TODO get from github same for .install files
		#for installer in self.installerJsonFiles(skillPath):
		#	data = self.validateSyntax(installer)
		#	if data and 'skill' in data['conditions']:
		#		for skill in data['conditions']['skill']:
		#			if skill['name'] != skillPath.name:
		#				path = self.searchSkill(skill['name'])
		#				pathSet = {path} if path else set()
		#				skills = skills.union(pathSet, self.getRequiredSkills(path))
		return skills



	def getAllSlots(self, language: str) -> dict:
		allSlots = dict()

		for dialogTemplate in self.getCoreSkillTemplates(language):
			allSlots.update(DialogTemplate(dialogTemplate).slots)

		for skill in self.getRequiredSkills():
			path = skill / 'dialogTemplate' / f'{language}.json'
			if path.is_file():
				data = self._files[path.stem]
				allSlots.update(DialogTemplate(data).slots)
		return allSlots


	@staticmethod
	def searchMissingSlotValues(values: list, slot: dict) -> list:
		if slot['automaticallyExtensible']:
			return list()

		allValues = list()
		for slotValue in slot['values']:
			allValues.append(unidecode(slotValue['value']).lower())
			allValues.extend([unidecode(x).lower() for x in slotValue.get('synonyms', list())])

		return [value for value in values if unidecode(value).lower() not in allValues]


	def validateIntentSlot(self, language: str, slot: str, values: list) -> Union[list,str]:
		if self.isSnipsBuiltinSlot(slot):
			return

		allSlots = self.getAllSlots(language)
		if slot in allSlots:
			return self.searchMissingSlotValues(values, allSlots[slot])

		return slot


	def validateIntentSlots(self) -> None:
		for file in self.jsonFiles:
			missingSlotValues = dict()
			missingSlots = list()
			data = self._files[file.stem]
			for intentName, slots in DialogTemplate(data).utteranceSlots.items():
				for slot, values in slots.items():
					result = self.validateIntentSlot(file.stem, slot, values)
					if isinstance(result, str):
						missingSlots.append(result)
						self._error = True
					elif result:
						missingSlotValues[slot] = result
						self._error = True
			
			if missingSlots:
				self.saveIndentedError(2, f'missing slots in {file.parent.name}/{file.name}:')
				self.saveIndentedError(4, intentName)
				self.printErrorList(missingSlots, 4)
			
			if missingSlotValues:
				self.saveIndentedError(2, f'missing slot values in {file.parent.name}/{file.name}:')
				for slot, missingValues in sorted(missingSlotValues.items()):
					self.saveIndentedError(8, f'intent: {intentName}, slot: {slot}')
					self.printErrorList(missingValues, 8)
			
		
	
	def validateIntents(self) -> None:
		allIntents = DialogTemplate(self._files['en']).intents

		# check whether the same intents appear in all files
		for file in self.jsonFiles:

			data = self._files[file.stem]
			missingIntents = [k for k in allIntents if k not in DialogTemplate(data).intents]
			if missingIntents:
				self.saveIndentedError(2, f'missing intent translation in {file.parent.name}/{file.name}:')
				self.printErrorList(missingIntents, 4)
				self._error = True


	def validateSlots(self) -> None:
		allSlots = DialogTemplate(self._files['en']).slots

		# check whether the same slots appear in all files
		for file in self.jsonFiles:
			data = self._files[file.stem]
			missingSlots = [k for k in allSlots if k not in DialogTemplate(data).slots]
			if missingSlots:
				self.saveIndentedError(2, f'missing slot translation in {file.parent.name}/{file.name}:')
				self.printErrorList(missingSlots, 4)
				self._error = True


	def searchDuplicateUtterances(self, verbosity: int) -> None:
		for file in self.jsonFiles:
			error = 0
			data = self._files[file.stem]
			for intentName, cleanedUtterances in DialogTemplate(data, verbosity).cleanedUtterances.items():
				for _, utterances in cleanedUtterances.items():
					if len(utterances) > 1:
						if not error:
							error = True
							self.saveIndentedError(2, f'duplicates in {file.parent.name}/{file.name}:')
						self.saveIndentedError(4, intentName)
						self.printErrorList(utterances, 4)

			self._error = self._error or error


	def loadFiles(self):
		for file in self.jsonFiles:
			data = self.validateSyntax(file)
			self._files[file.stem] = data


	def validate(self, verbosity: int = 0) -> bool:
		self.loadFiles()
		if self._files['en']:
			self.validateJsonSchemas()
			if self._error:
				return self._error
			self.validateSlots()
			self.validateIntents()

			self.searchDuplicateUtterances(verbosity)
			self.validateIntentSlots()
		return self._error
