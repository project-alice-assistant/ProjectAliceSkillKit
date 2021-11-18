#  Copyright (c) 2021
#
#  This file, create.py, is part of Project Alice.
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

from __future__ import print_function, unicode_literals

import click
import jinja2
import json
import os
import shutil
from PyInquirer import ValidationError, Validator, prompt
from pathlib import Path
from typing import Union

from AliceGit.Git import Repository
from AliceGit.Github import Github


class SkillCreationFailed(Exception):

	def __init__(self, msg: Exception):
		super().__init__(msg)


# noinspection PyShadowingNames
class SkillCreator:

	SEPARATOR = '\n----------------------------\n'

	def __init__(self, fromFile: Path = None, skillPath: Path = None, widgetName: str = None, deviceTypeName: str = None, nodeName: str = None):
		self._skillPath = skillPath
		self._general = dict()
		self._fromFile = fromFile
		self._widgetName = widgetName
		self._deviceTypeName = deviceTypeName
		self._nodeName = nodeName


	def start(self):
		if self._fromFile:
			try:
				return self.createFromFile()
			except:
				return False
		if self._skillPath:
			#fill the information form the given installFile - abort if no file is found
			if not self.fillDataFromInstallFile():
				return False

			if self._widgetName:
				return self.makeWidgets([self._widgetName])
			if self._deviceTypeName:
				return self.makeDevices([self._deviceTypeName])
			if self._nodeName:
				return self.makeScenarioNodes([self._nodeName])

		print(' _____ _    _ _ _   _   ___ _   ')
		print('/  ___| |  (_) | | | | / (_) |  ')
		print('\ `--.| | ___| | | | |/ / _| |_ ')
		print(' `--. \ |/ / | | | |    \| | __|')
		print('/\__/ /   <| | | | | |\  \ | |_ ')
		print('\____/|_|\_\_|_|_| \_| \_/_|\__|')
		print('\nWelcome in the skill creation tool')
		print('This tool will help you in creating a new skill\n')
		print("Did you know that you can also create skills via Alice's web interface?\n")

		self.generalQuestions()
		self.createDestinationFolder()
		self.createBaseFiles()
		self.createInstructions()
		self.createDialogTemplates()
		self.createTalks()
		self.createInstallFile()
		self.createReadme()
		self.createWidgets()
		self.createScenarioNodes()
		self.createDevices()
		self.uploadGithub()

		print(self.SEPARATOR)
		print('All done!')
		print(f"You can now start creating your skill. You will find your skill in {Path(self._skillPath)}")
		print('\nRemember to edit the generated files to remove the dummy data!!\n')
		print('Thank you for creating for Project Alice')


	def fillDataFromInstallFile(self) -> bool:
		installs = list(self._skillPath.glob('*.install'))
		if len(installs) != 1:
			return False
		install = installs[0]
		data = json.loads(install.read_text())
		self._general['skillName'] = data['name']
		self._general['langs'] = data['conditions']['lang']
		return True


	def createFromFile(self) -> bool:
		if not self._fromFile.exists():
			raise SkillCreationFailed(Exception('Data file not found'))

		data = json.loads(self._fromFile.read_text())

		try:
			self._general = {
				'username'          : data['username'],
				'skillName'         : data['skillName'],
				'speakableName'     : data['speakableName'],
				'category'          : data['category'],
				'description'       : data['description'],
				'langs'             : data['langs'],
				'createInstructions': data['createInstructions']
			}

			self._skillPath = Path.home() / 'ProjectAliceSkillKit' / self._general['username'] / self._general['skillName']
			shutil.rmtree(self._skillPath, ignore_errors=True)

			self.createDestinationFolder()
			self.createBaseFiles()
			self.createInstructions()
			self.createDialogTemplates()
			self.createTalks()

			install = {
				'name'              : self._general['skillName'],
				'speakableName'     : self._general['speakableName'],
				'version'           : '0.0.1',
				'icon'              : 'fab fa-battle-net',
				'category'          : self._general['category'],
				'author'            : self._general['username'],
				'maintainers'       : [],
				'desc'              : self._general['description'],
				'aliceMinVersion'   : '1.0.0-rc1',
				'pipRequirements'   : data['pipreq'],
				'systemRequirements': data['sysreq'],
				'conditions'        : data['conditions']
			}

			# Make file nicer
			installFile = Path(self._skillPath, f'{self._general["skillName"]}.install')
			installFile.write_text(json.dumps(install, ensure_ascii=False, indent='\t'))

			self.createReadme()
			self.makeWidgets(data.get('widgets', list()))
			self.makeScenarioNodes(data.get('scenarioNodes', list()))
			self.makeDevices(data.get('devices', list()))

			shutil.move(self._skillPath, Path(data['outputDestination']))

		except Exception as e:
			raise SkillCreationFailed(e)

		return True


	def generalQuestions(self):
		answers = prompt(FIRST_QUESTION)

		self._skillPath = Path.home() / 'ProjectAliceSkillKit' / answers['username'] / answers['skillName']

		while self._skillPath.exists():
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'delete',
					'message': 'Seems like this skill name already exists.\nDo you want to delete it locally?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'skillName',
					'message' : 'Ok, so chose another skill name please',
					'validate': NotEmpty,
					'filter'  : lambda val: str(val).title().replace(' ', ''),
					'when'    : lambda subAnswers: not subAnswers['delete']
				}
			]
			subAnswers = prompt(questions)
			if subAnswers['delete']:
				shutil.rmtree(path=self._skillPath)
			else:
				self._skillPath = Path.home() / 'ProjectAlice/skills/' / subAnswers['skillName']
				answers['skillName'] = subAnswers['skillName']

		subAnswers = prompt(NEXT_QUESTION)
		self._general = {**answers, **subAnswers}


	def createTemplateFile(self, outputPath: Union[Path, str], templateFile: str, **kwargs):
		if isinstance(outputPath, str):
			outputPath = Path(outputPath)
		templateLoader = jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), 'templates'))
		templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
		template = templateEnv.get_template(templateFile)
		(self._skillPath / outputPath).write_text(template.render(**kwargs))


	def createDirectories(self, directories: list, isRelative: bool = True):
		for directory in directories:
			if isRelative:
				(self._skillPath / directory).mkdir(parents=True, exist_ok=True)
			else:
				directory.mkdir(parents=True, exist_ok=True)

	def createFiles(self, files: list):
		for file in files:
			(self._skillPath / file).touch(exist_ok=True)


	def createDestinationFolder(self):
		print(self.SEPARATOR)
		print('Creating destination folders')

		self.createDirectories([
			'dialogTemplate',
			'talks'
		])

		self.createDirectories([
			Path(self._skillPath, '.github/workflows')
		], False)


	def createInstallFile(self):
		questions = [
			{
				'type'   : 'confirm',
				'name'   : 'isOnline',
				'message': 'Does your skill need internet connectivity?',
				'default': False
			},
			{
				'type'   : 'confirm',
				'name'   : 'arbitraryCapture',
				'message': 'Does your skill need the ASR to capture arbitrary text?',
				'default': False
			}
		]

		answers = prompt(questions)

		reqs = list()
		while True:
			questions = [{
					'type'   : 'confirm',
					'name'   : 'requirements',
					'message': 'Do you want to add python pip requirements?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'req',
					'message' : 'Enter the pip requirement name or `stop` to cancel',
					'validate': NotEmpty,
					'when'    : lambda subAnswers: subAnswers['requirements']
				}
			]
			subAnswers = prompt(questions)
			if not subAnswers['requirements'] or subAnswers['req'] == 'stop':
				break
			reqs.append(subAnswers['req'])

		sysreqs = list()
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'sysrequirements',
					'message': 'Do you want to add system requirements?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'sysreq',
					'message' : 'Enter the requirement name or `stop` to cancel',
					'validate': NotEmpty,
					'when'    : lambda subAnswers: subAnswers['sysrequirements']
				}
			]
			subAnswers = prompt(questions)
			if not subAnswers['sysrequirements'] or subAnswers['sysreq'] == 'stop':
				break
			sysreqs.append(subAnswers['sysreq'])

		neededSkills = list()
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'neededSkills',
					'message': 'Are there any skills that are REQUIRED for yours to run?' if not neededSkills else 'Any other?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'skills',
					'message' : 'Enter the skill name or `stop` to cancel',
					'validate': NotEmpty,
					'when'    : lambda subAnswers: subAnswers['neededSkills']
				}
			]
			subAnswers = prompt(questions)
			if not subAnswers['neededSkills'] or subAnswers['skills'] == 'stop':
				break
			neededSkills.append(subAnswers['skills'])

		conflictingSkills = list()
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'conflictingSkills',
					'message': 'Are there any skills that are CONFLICTING with yours?' if not conflictingSkills else 'Any other?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'conflictSkills',
					'message' : 'Enter the skill name or `stop` to cancel',
					'validate': NotEmpty,
					'when'    : lambda subAnswers: subAnswers['conflictingSkills']
				}
			]
			subAnswers = prompt(questions)
			if not subAnswers['conflictingSkills'] or subAnswers['conflictSkills'] == 'stop':
				break
			conflictingSkills.append(subAnswers['conflictSkills'])

		conditions = dict()
		conditions['lang'] = self._general['langs']
		if answers['isOnline']:
			conditions['online'] = answers['isOnline']

		if answers['arbitraryCapture']:
			conditions['asrArbitraryCapture'] = answers['arbitraryCapture']

		if neededSkills:
			conditions['skill'] = neededSkills

		if conflictingSkills:
			conditions['notSkill'] = conflictingSkills

		print(self.SEPARATOR)
		print('Creating install file')

		install = {
			'name'              : self._general['skillName'],
			'speakableName'     : self._general['speakableName'],
			'version'           : '0.0.1',
			'icon'              : 'fab fa-battle-net',
			'category'          : self._general['category'],
			'author'            : self._general['username'],
			'maintainers'       : [],
			'desc'              : self._general['description'],
			'aliceMinVersion'   : '1.0.0-b3',
			'pipRequirements'   : reqs,
			'systemRequirements': sysreqs,
			'conditions'        : conditions
		}

		# Make file nicer
		installFile = Path(self._skillPath, f'{self._general["skillName"]}.install')
		installFile.write_text(json.dumps(install, ensure_ascii=False, indent='\t'))


	def createDialogTemplates(self):
		print('Creating dialog templates')
		for lang in self._general['langs']:
			print(f'- {lang}')
			self.createTemplateFile(f'dialogTemplate/{lang}.json', 'dialog.json.j2',
			                        skillName=self._general['skillName'],
			                        username=self._general['username']
			                        )

			self.createTemplateFile(f'dialogTemplate/{lang}.sample', 'sample.json.j2')


	def createTalks(self):
		print('Creating talk files')
		for lang in self._general['langs']:
			print(f'- {lang}')
			self.createTemplateFile(f'talks/{lang}.json', 'talks.json.j2')

		print(self.SEPARATOR)


	def createReadme(self):
		print('Creating readme file')
		langs = ','.join([f'\n\t\t\t"{lang}"' for lang in self._general['langs']])
		if langs:
			langs += '\n\t\t'
		self.createTemplateFile('README.md', 'README.md.j2',
		                        skillName=self._general['skillName'],
		                        description=self._general['description'],
		                        username=self._general['username'],
		                        langs=self._general['langs']
		                        )
		print(self.SEPARATOR)


	def createBaseFiles(self):
		print('Creating python main class')
		self.createTemplateFile(f"{self._general['skillName']}.py", 'skill.py.j2',
		                        skillName=self._general['skillName'],
		                        description=self._general['description'],
		                        username=self._general['username']
		                        )

		print('Creating base files')
		self.createTemplateFile(
			outputPath=self._skillPath / '.gitignore',
			templateFile='.gitignore.j2'
		)

		self.createTemplateFile(
			outputPath=self._skillPath / 'LICENSE',
			templateFile='LICENSE.j2'
		)

		self.createTemplateFile(
			outputPath=self._skillPath / '.gitlab-ci.yml',
			templateFile='.gitlab-ci.yml.j2'
		)

		self.createTemplateFile(
			outputPath=self._skillPath / 'mypy.ini',
			templateFile='mypy.ini'
		)

		self.createTemplateFile(
			outputPath=self._skillPath / 'sonar-project.properties',
			templateFile='sonar-project.properties.j2',
			skillName=self._general['skillName']
		)

		self.createTemplateFile(
			outputPath=self._skillPath / '.editorconfig',
			templateFile='.editorconfig'
		)

		self.createTemplateFile(
			outputPath=Path(self._skillPath, '.github/workflows/tests.yml'),
			templateFile='tests.yml.j2'
		)

		self.createTemplateFile(
			outputPath=Path(self._skillPath, '.github/PULL_REQUEST_TEMPLATE.md'),
			templateFile='PULL_REQUEST_TEMPLATE.md'
		)


	def createInstructions(self) -> bool:
		if not self._general['createInstructions']:
			return False

		print('Creating instruction files')
		self.createDirectories(['instructions'])
		files = list()
		for lang in self._general['langs']:
			print(f'- {lang}')
			files.append(f'instructions/{lang}.md')
		self.createFiles(files)
		return True


	def createDevices(self) -> bool:
		skillDevices = []
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'devices',
					'message': 'Are you planning on creating devices for your skill?' if not skillDevices else 'Any other devices?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'device',
					'message' : 'Enter the name of the device',
					'validate': NotEmpty,
					'when'    : lambda subAnswers: subAnswers['devices']
				}
			]
			subAnswers = prompt(questions)
			if not subAnswers['devices'] or subAnswers['device'] == 'stop':
				break
			skillDevices.append(subAnswers['device'])

		if not skillDevices:
			return False

		return self.makeDevices(skillDevices)


	def makeDevices(self, skillDevices: list) -> bool:
		if not skillDevices:
			return False

		print('Creating devices base directories')
		self.createDirectories([
			'devices/img'
		])

		print('Creating devices files')
		self.createFiles([
			'devices/__init__.py',
			'widgets/img/.gitkeep',
		])

		for device in skillDevices:
			device = toPascalCase(device, True)
			self.createTemplateFile(f'devices/{device}.py', 'devices/device.py.j2', device=device)
			self.createTemplateFile(f'devices/{device}.config.template', 'devices/device.config.template.j2')

		return True


	def createWidgets(self) -> bool:
		skillWidgets = []
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'widgets',
					'message': 'Are you planning on creating widgets for your skill? Widgets are used on the\ninterface to display quick informations that your skill can return' if not skillWidgets else 'Any other widgets?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'widget',
					'message' : 'Enter the name of the widget',
					'validate': NotEmpty,
					'when'    : lambda subAnswers: subAnswers['widgets']
				}
			]
			subAnswers = prompt(questions)
			if not subAnswers['widgets'] or subAnswers['widget'] == 'stop':
				break
			skillWidgets.append(subAnswers['widget'])

		if not skillWidgets:
			return False

		return self.makeWidgets(skillWidgets)


	def makeWidgets(self, skillWidgets: list) -> bool:
		if not skillWidgets:
			return False

		print('Creating widgets base directories')
		self.createDirectories([
			'widgets/css',
			'widgets/img',
			'widgets/js',
			'widgets/lang',
			'widgets/templates'
		])

		print('Creating widgets files')
		self.createFiles([
			'widgets/__init__.py',
			'widgets/img/.gitkeep'
		])

		for widget in skillWidgets:
			widget = str(widget).title().replace(' ', '')
			self.createTemplateFile(f'widgets/css/{widget}.css', 'widgets/widget.css.j2', widgetName=widget)
			self.createTemplateFile(f'widgets/js/{widget}.js', 'widgets/widget.js.j2', widget=widget, skill=self._skillPath.stem)
			self.createTemplateFile(f'widgets/templates/{widget}.html', 'widgets/widget.html.j2', widget=widget, skill=self._skillPath.stem)
			self.createTemplateFile(f'widgets/{widget}.py', 'widgets/widget.py.j2', widget=widget)
			(self._skillPath / f'widgets/lang/{widget}.lang.json').write_text('{}')

		return True


	def createScenarioNodes(self) -> bool:
		skillNodes = []
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'nodes',
					'message': 'Are you planning on creating scenario nodes? Scenario nodes are used on the\ninterface for users to create interactions between skills!' if not skillNodes else 'Any other node?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'node',
					'message' : 'Enter the name of the node',
					'validate': NotEmpty,
					'filter'  : lambda val: str(val)[0].lower() + str(val).title().replace(' ', '')[1:],
					'when'    : lambda subAnswers: subAnswers['nodes']
				}
			]
			subAnswers = prompt(questions)
			if not subAnswers['nodes'] or subAnswers['node'] == 'stop':
				break
			skillNodes.append(subAnswers['node'])

		if not skillNodes:
			return False

		return self.makeScenarioNodes(skillNodes)


	def makeScenarioNodes(self, skillNodes: list) -> bool:
		if not skillNodes:
			return False

		print('Creating scenario nodes base directories')
		self.createDirectories([f'scenarioNodes/locales/{lang}' for lang in self._general['langs']])

		print('Creating scenario nodes files')
		self.createTemplateFile(f'scenarioNodes/package.json', 'nodes/package.json.j2', skillName=self._general['skillName'].lower(), username=self._general['username'], nodes=skillNodes)
		for nodeName in skillNodes:
			self.createTemplateFile(f'scenarioNodes/{nodeName}.js', 'nodes/node.js.j2', nodeName=nodeName)
			self.createTemplateFile(f'scenarioNodes/{nodeName}.html', 'nodes/node.html.j2', nodeName=nodeName, skillName=self._general['skillName'])

			for lang in self._general['langs']:
				self.createTemplateFile(f'scenarioNodes/locales/{lang}/{nodeName}.json', 'nodes/locales.json.j2',
										nodeName=nodeName)
		return True


	def uploadGithub(self) -> bool:
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'uploadToGithub',
					'message': 'The Skill Kit can upload your skill to Github. You need\n a Github account for that. Do you wish to upload your skill?',
					'default': False
				},
				{
					'type'    : 'password',
					'name'    : 'githubToken',
					'message' : 'Please enter your Github TOKEN (not password!)',
					'validate': NotEmpty,
					'when'    : lambda subAnswers: subAnswers['uploadToGithub']
				}
			]
			subAnswers = prompt(questions)
			if not subAnswers['uploadToGithub'] or subAnswers['githubToken']:
				break

		if subAnswers['uploadToGithub']:
			result = uploadSkillToGithub(
				githubToken=subAnswers['githubToken'],
				skillAuthor=self._general['username'],
				skillName=self._general["skillName"],
				skillPath=self._skillPath,
				skillDesc=self._general['description']
			)
			if not result:
				print('\nUnfortunately something went wrong uploading your skill. You can always do it manually!')
				return False
			else:
				print('\nYour skill was uploaded to your Github account!')
				return True


# STYLE = style_from_dict({
# 	Token.QuestionMark: '#996633 bold',
# 	Token.Selected    : '#5F819D bold',
# 	Token.Instruction : '#99ff33 bold', #NOSONAR
# 	Token.Pointer     : '#673ab7 bold',
# 	Token.Answer      : '#0066ff bold',
# 	Token.Question    : '#99ff33 bold',
# 	Token.Input       : '#99ff33 bold'
# })

class NotEmpty(Validator):

	def validate(self, document):
		if not document.text:
			raise ValidationError(
				message='This cannot be empty',
				cursor_position=len(document.text)
			)


FIRST_QUESTION = [
	{
		'type'    : 'input',
		'name'    : 'username',
		'message' : 'Please enter your Github user name',
		'validate': NotEmpty,
		'filter'  : lambda val: str(val).replace(' ', '')
	},
	{
		'type'    : 'input',
		'name'    : 'skillName',
		'message' : 'Please enter the name of the skill you are creating',
		'validate': NotEmpty,
		'filter'  : lambda val: ''.join(x.capitalize() for x in val.split(' '))
	}
]

NEXT_QUESTION = [
	{
		'type'    : 'input',
		'name'    : 'speakableName',
		'message' : 'Please enter the name of the skill in a form that can be spoken',
		'validate': NotEmpty
	},
	{
		'type'    : 'input',
		'name'    : 'description',
		'message' : 'Please enter a description for this skill',
		'validate': NotEmpty,
		'filter'  : lambda val: str(val).capitalize()
	},
	{
		'type'   : 'list',
		'name'   : 'category',
		'message': 'Please select in which category your skill belongs',
		'choices': ['weather', 'information', 'entertainment', 'music', 'game', 'kid', 'automation', 'assistance', 'security', 'planning', 'shopping', 'organisation', 'household', 'health'],
		'filter' : lambda val: val.lower()
	},
	{
		'type'    : 'checkbox',
		'name'    : 'langs',
		'message' : 'Choose the language for this skill. Note that to share\nyour skill on the official repo english is mandatory',
		'validate': NotEmpty,
		'choices' : [
			{
				'name'   : 'en',
				'checked': True
			},
			{
				'name': 'fr'
			},
			{
				'name': 'de'
			},
			{
				'name': 'it'
			},
			{
				'name': 'pl'
			},
			{
				'name': 'es'
			},
			{
				'name': 'jp'
			},
			{
				'name': 'kr'
			},
		]
	},
	{
		'type'   : 'confirm',
		'name'   : 'createInstructions',
		'message': 'Would you like to create instructions for your skill?\nInstructions display on the interface and let users know how to use your skill.',
		'default': False
	}
]


def toPascalCase(theString: str, replaceSepCharacters: bool = False, sepCharacters: tuple = None) -> str:
	if replaceSepCharacters:
		for char in sepCharacters or ('-', '_'):
			theString = theString.replace(char, ' ')

	return ''.join(x.capitalize() for x in theString.split(' '))


def uploadSkillToGithub(githubToken: str, skillAuthor: str, skillName: str, skillPath: Path, skillDesc: str) -> bool:
	try:
		print(f'Uploading {skillName} to Github')

		if not skillPath.exists():
			raise Exception("Local skill doesn't exist")

		data = {
			'name'       : f'skill_{skillName}',
			'description': skillDesc,
			'has-issues' : True,
			'has-wiki'   : False
		}

		try:
			github = Github(username=skillAuthor, token=githubToken, repositoryName=data['name'], createRepository=True, options=data)
		except:
			raise

		remote = f'https://{skillAuthor}:{githubToken}@github.com/{skillAuthor}/skill_{skillName}.git'
		try:
			repository = Repository(directory=skillPath, init=True, url=remote)
		except:
			raise

		repository.remoteAdd(url=remote)
		repository.config(key='user.email', value='githubbot@projectalice.io')
		repository.config(key='user.name', value='ProjectAliceBot')
		repository.commit(message='Initial upload by Project Alice Skill Kit', autoAdd=True)
		repository.push()
		print(f'Skill uploaded! You can find it on {github.url}')
		return True
	except Exception as e:
		print(f'Something went wrong uploading the skill on Github: {e}')
		return False


@click.command()
@click.option('-f', '--file', default=None, show_default=True, help='Path to a json data file')
def create(file: str = ''):
	"""
	Creates a new skill
	"""
	if file:
		file = Path(file)
	if SkillCreator(file).start():
		exit(0)
	else:
		exit(1)


@click.command()
@click.option('-w', '--widget', default=None, show_default=True, help='Widget to be added')
@click.option('-p', '--path', default=None, show_default=True, help='Target path, the skills directory')
def createWidget(widget: str = None, path: str = None):
	"""
	create the widget structure for an existing skill
	"""
	if widget is None or path is None:
		raise Exception('Missing parameters to create widget')

	skillPath = Path(path)
	if SkillCreator(widgetName=widget, skillPath=skillPath).start():
		exit(0)
	else:
		exit(1)


@click.command()
@click.option('-d', '--device', default=None, show_default=True, help='DeviceType to be added')
@click.option('-p', '--path', default=None, show_default=True, help='Target path, the skill directory')
def createDeviceType(device: str = None, path: str = None):
	"""
	create the deviceType structure for an existing skill
	"""
	if device is None or path is None:
		raise Exception('Missing parameters to create device type')

	skillPath = Path(path)
	if SkillCreator(deviceTypeName=device, skillPath=skillPath).start():
		exit(0)
	else:
		exit(1)


@click.command()
@click.option('-n', '--node', default=None, show_default=True, help='Scenario Node to be added')
@click.option('-p', '--path', default=None, show_default=True, help='Target path, the skill directory')
def createNode(node: str = None, path: str = None):
	"""
	create the scenario node structure for an existing skill
	"""
	if node is None or path is None:
		raise Exception('Missing parameters to create node')

	skillPath = Path(path)
	if SkillCreator(nodeName=node, skillPath=skillPath).start():
		exit(0)
	else:
		exit(1)


@click.command()
@click.option('-t', '--token', default=None, show_default=False, help='Your Github token')
@click.option('-a', '--author', default=None, show_default=False, help='Your Github username')
@click.option('-p', '--path', default=None, show_default=False, help='Path to the skill directory')
@click.option('-d', '--desc', default=None, show_default=False, help='Skill description for Github')
def uploadToGithub(github_token: str, skill_author: str, skill_path: str, skill_desc: str): #NOSONAR
	skillPath = Path(skill_path)
	if not skillPath.exists():
		raise Exception('Invalid skill path')

	skillName = skillPath.stem
	if uploadSkillToGithub(githubToken=github_token, skillAuthor=skill_author, skillName=skillName, skillPath=skillPath, skillDesc=skill_desc):
		exit(0)
	else:
		exit(1)


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	create()
