from __future__ import print_function, unicode_literals

import os
import shutil
from pathlib import Path

import click
import jinja2
from PyInquirer import Token, ValidationError, Validator, prompt, style_from_dict


class SkillCreator:

	def __init__(self):
		self._skillPath = None
		self._general = None


	def start(self):
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
		self.createInstallFile()
		self.createDialogTemplates()
		self.createTalks()
		self.createReadme()
		self.createWidgets()
		self.createScenarioNodes()

		print('----------------------------\n')
		print('All done!')
		print(f"You can now start creating your skill. You will find the main class in {Path(self._skillPath, self._general['skillName']).with_suffix('.py')}")
		print('\nRemember to edit the dialogTemplate/XYZ.json and remove the dummy data!!\n')
		print('Thank you for creating for Project Alice')


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
				self._skillPath = Path.home() / 'ProjectAliceSkillKit' / answers['username'] / subAnswers['skillName']
				answers['skillName'] = subAnswers['skillName']

		subAnswers = prompt(NEXT_QUESTION, style=STYLE)
		self._general = {**answers, **subAnswers}


	def createTemplateFile(self, outputPath: str, templateFile: str, **kwargs):
		templateLoader = jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), 'templates'))
		templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
		template = templateEnv.get_template(templateFile)
		(self._skillPath / outputPath).write_text(template.render(**kwargs))


	def createDirectories(self, directories: list):
		for directory in directories:
			(self._skillPath / directory).mkdir(parents=True, exist_ok=True)


	def createFiles(self, files: list):
		for file in files:
			(self._skillPath / file).touch(exist_ok=True)


	def createDestinationFolder(self):
		print('\n----------------------------')
		print('Creating destination folders')

		self.createDirectories([
			'dialogTemplate',
			'talks'
		])

		print('Creating python class')
		self.createTemplateFile(f"{self._general['skillName']}.py", 'skill.py.j2',
		                        skillName=self._general['skillName'],
		                        description=self._general['description'],
		                        username=self._general['username']
		                        )


	def createInstallFile(self):
		reqs = list()
		while True:
			questions = [
				{
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

		print('Creating install file')
		langs = ','.join([f'\n\t\t\t"{lang}"' for lang in self._general['langs']])
		if langs:
			langs += '\n\t\t'

		pipRequirements = ','.join([f'\n\t\t"{req}"' for req in reqs])
		if pipRequirements:
			pipRequirements += '\n\t'

		systemRequirements = ','.join([f'\n\t\t"{req}"' for req in sysreqs])
		if systemRequirements:
			systemRequirements += '\n\t'

		self.createTemplateFile(f"{self._general['skillName']}.install", 'install.j2',
		                        skillName=self._general['skillName'],
		                        description=self._general['description'],
		                        username=self._general['username'],
		                        langs=self._general['langs'],
		                        pipRequirements=reqs,
		                        systemRequirements=sysreqs
		                        )


	def createDialogTemplates(self):
		print('Creating dialog template(s)')
		for lang in self._general['langs']:
			print(f'- {lang}')
			self.createTemplateFile(f'dialogTemplate/{lang}.json', 'dialog.json.j2',
			                        skillName=self._general['skillName'],
			                        username=self._general['username']
			                        )


	def createTalks(self):
		print('Creating talks')
		for lang in self._general['langs']:
			print(f'- {lang}')
			self.createTemplateFile(f'talks/{lang}.json', 'talks.json.j2')


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


	def createWidgets(self):
		skillWidgets = []
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'widgets',
					'message': 'Are you planning on creating widgets for you skill? Widgets are used on the\ninterface to display quick informations that your skill can return' if not skillWidgets else 'Any other widgets?',
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

		print('Creating widgets base directories')
		self.createDirectories([
			'widgets/css',
			'widgets/fonts',
			'widgets/img',
			'widgets/js',
			'widgets/lang',
			'widgets/templates'
		])

		print('Creating widgets files')
		self.createFiles([
			'widgets/__init__.py',
			'widgets/css/common.css',
			'widgets/img/.gitkeep',
			'widgets/fonts/.gitkeep'
		])

		for widget in skillWidgets:
			widget = str(widget).title().replace(' ', '')
			self.createTemplateFile(f'widgets/css/{widget}.css', 'widget.css.j2', widgetName=widget)
			self.createTemplateFile(f'widgets/js/{widget}.js', 'widget.js.j2')
			self.createTemplateFile(f'widgets/templates/{widget}.html', 'widget.html.j2', widget=widget)
			self.createTemplateFile(f'widgets/{widget}.py', 'widget.py.j2', widget=widget)
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

		print('Creating scenario nodes base directories')
		self.createDirectories([f'scenarioNodes/locales/{lang}' for lang in self._general['langs']])

		print('Creating scenario nodes files')
		self.createTemplateFile(f'scenarioNodes/package.json', 'nodes/package.json.j2', skillName=self._general['skillName'].lower(), username=self._general['username'], nodes=skillNodes)
		for nodeName in skillNodes:
			self.createTemplateFile(f'scenarioNodes/{nodeName}.js', 'nodes/node.js.j2', nodeName=nodeName)
			self.createTemplateFile(f'scenarioNodes/{nodeName}.html', 'nodes/node.html.j2', nodeName=nodeName, skillName=self._general['skillName'])

			for lang in self._general['langs']:
				self.createTemplateFile(f'scenarioNodes/locales/{lang}/{nodeName}.js', 'nodes/locales.json.j2', nodeName=nodeName)


STYLE = style_from_dict({
	Token.QuestionMark: '#996633 bold',
	Token.Selected    : '#5F819D bold',
	Token.Instruction : '#99ff33 bold',
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
		'filter'  : lambda val: str(val).capitalize().replace(' ', '')
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
		'name'    : 'description',
		'message' : 'Please enter a description for this skill',
		'validate': NotEmpty,
		'filter'  : lambda val: str(val).capitalize()
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
				'name': 'es'
			},
			{
				'name': 'it'
			},
			{
				'name': 'jp'
			},
			{
				'name': 'kr'
			},
		]
	}
]


@click.command()
def create():
	"""
	creates a new skill
	"""
	SkillCreator().start()
