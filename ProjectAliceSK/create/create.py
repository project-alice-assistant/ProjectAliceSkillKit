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
import requests
import shutil
import subprocess
from PyInquirer import Token, ValidationError, Validator, prompt, style_from_dict
from pathlib import Path


class SkillCreationFailed(Exception):

	def __init__(self, msg: Exception):
		super().__init__(msg)


# noinspection PyShadowingNames
class SkillCreator:

	SEPARATOR = '\n----------------------------\n'

	def __init__(self, fromFile: Path = None):
		self._skillPath = None
		self._general = None
		self._fromFile = fromFile


	def start(self):
		if self._fromFile:
			return self.createFromFile()

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
				'aliceMinVersion'   : '1.0.0-b5',
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
		answers = prompt(FIRST_QUESTION, style=STYLE)

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
			subAnswers = prompt(questions, style=STYLE)
			if subAnswers['delete']:
				shutil.rmtree(path=self._skillPath)
			else:
				self._skillPath = Path.home() / 'ProjectAlice/skills/' / subAnswers['skillName']
				answers['skillName'] = subAnswers['skillName']

		subAnswers = prompt(NEXT_QUESTION, style=STYLE)
		self._general = {**answers, **subAnswers}


	def createTemplateFile(self, outputPath: str, templateFile: str, **kwargs):
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

		answers = prompt(questions, style=STYLE)

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
			subAnswers = prompt(questions, style=STYLE)
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
			subAnswers = prompt(questions, style=STYLE)
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
			subAnswers = prompt(questions, style=STYLE)
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
			subAnswers = prompt(questions, style=STYLE)
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


	def createInstructions(self):
		if not self._general['createInstructions']:
			return

		print('Creating instruction files')
		self.createDirectories(['instructions'])
		files = list()
		for lang in self._general['langs']:
			print(f'- {lang}')
			files.append(f'instructions/{lang}.md')
		self.createFiles(files)


	def createDevices(self):
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
			subAnswers = prompt(questions, style=STYLE)
			if not subAnswers['devices'] or subAnswers['device'] == 'stop':
				break
			skillDevices.append(subAnswers['device'])

		if not skillDevices:
			return

		self.makeDevices(skillDevices)


	def makeDevices(self, skillDevices: list):
		if not skillDevices:
			return

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


	def createWidgets(self):
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
			subAnswers = prompt(questions, style=STYLE)
			if not subAnswers['widgets'] or subAnswers['widget'] == 'stop':
				break
			skillWidgets.append(subAnswers['widget'])

		if not skillWidgets:
			return

		self.makeWidgets(skillWidgets)


	def makeWidgets(self, skillWidgets: list):
		if not skillWidgets:
			return

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


	def createScenarioNodes(self):
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
			subAnswers = prompt(questions, style=STYLE)
			if not subAnswers['nodes'] or subAnswers['node'] == 'stop':
				break
			skillNodes.append(subAnswers['node'])

		if not skillNodes:
			return

		self.makeScenarioNodes(skillNodes)


	def makeScenarioNodes(self, skillNodes: list):
		if not skillNodes:
			return

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


	def uploadGithub(self):
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
			subAnswers = prompt(questions, style=STYLE)
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
			else:
				print('\nYour skill was uploaded to your Github account!')


STYLE = style_from_dict({
	Token.QuestionMark: '#996633 bold',
	Token.Selected    : '#5F819D bold',
	Token.Instruction : '#99ff33 bold', #NOSONAR
	Token.Pointer     : '#673ab7 bold',
	Token.Answer      : '#0066ff bold',
	Token.Question    : '#99ff33 bold',
	Token.Input       : '#99ff33 bold'
})


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
		req = requests.post('https://api.github.com/user/repos', data=json.dumps(data), auth=(skillAuthor, githubToken))

		if req.status_code != 201:
			raise Exception("Couldn't create the repository on Github")

		subprocess.run(f'git -C {str(skillPath)} init'.split())

		subprocess.run(['git', '-C', str(skillPath), 'config', 'user.email', 'githubbot@projectalice.io'])
		subprocess.run(['git', '-C', str(skillPath), 'config', 'user.name', 'ProjectAliceBot'])

		remote = f'https://{skillAuthor}:{githubToken}@github.com/{skillAuthor}/skill_{skillName}.git'
		subprocess.run(['git', '-C', str(skillPath), 'remote', 'add', 'origin', remote])

		subprocess.run(['git', '-C', str(skillPath), 'add', '--all'])
		subprocess.run(['git', '-C', str(skillPath), 'commit', '-m', '"Initial upload by Project Alice Skill Kit"'])
		subprocess.run(['git', '-C', str(skillPath), 'push', '--set-upstream', 'origin', 'master'])

		url = f'https://github.com/{skillAuthor}/skill_{skillName}.git'
		print(f'Skill uploaded! You can find it on {url}')
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
	SkillCreator(file).start()


if __name__ == '__main__':
	# pylint: disable=no-value-for-parameter
	create()
