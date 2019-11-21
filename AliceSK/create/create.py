from __future__ import print_function, unicode_literals

import shutil
from pathlib import Path
import click
import os

from PyInquirer import style_from_dict, Token, prompt, Validator, ValidationError
import jinja2

class Moduler:
	def __init__(self):
		self._modulePath = None
		self._general = None
		

	def start(self):
		print('\nHey welcome in this basic module creation tool!')
		self.generalQuestions()
		self.createDestinationFolder()
		self.createInstallFile()
		self.createDialogTemplates()
		self.createTalks()
		self.createReadme()
		self.createWidgets
	
		print('----------------------------\n')
		print('All done!')
		print(f"You can now start creating your module. You will find the main class in {self._modulePath}/{self._general['moduleName']}.py")
		print('\nRemember to edit the dialogTemplate/XYZ.json and remove the dummy data!!\n')
		print('Thank you for creating for Project Alice')


	def generalQuestions(self):
		answers = prompt(FIRST_QUESTION, style=STYLE)

		self._modulePath = Path.home() / 'ProjectAliceModuler' / answers['username'] / answers['moduleName']

		while self._modulePath.exists():
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'delete',
					'message': 'Seems like this module name already exists.\nDo you want to delete it locally?',
					'default': False
				},
				{
					'type'    : 'input',
					'name'    : 'moduleName',
					'message' : 'Ok, so chose another module name please',
					'validate': NotEmpty,
					'filter'  : lambda val: str(val).title().replace(' ', ''),
					'when'    : lambda subAnswers: not subAnswers['delete']
				}
			]
			subAnswers = prompt(questions, style=STYLE)
			if subAnswers['delete']:
				shutil.rmtree(path=self._modulePath)
			else:
				self._modulePath = Path.home() / 'ProjectAliceModuler' / answers['username'] / subAnswers['moduleName']
				answers['moduleName'] = subAnswers['moduleName']

		subAnswers = prompt(NEXT_QUESTION, style=STYLE)
		self._general = {**answers, **subAnswers}


	def createTemplateFile(self, outputPath: str, templateFile: str, **kwargs) -> str:
		templateLoader = jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), 'templates'))
		templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
		template = templateEnv.get_template(templateFile)
		(self._modulePath / outputPath).write_text(template.render(**kwargs))


	def createDirectories(self, directories: list):
		for directory in directories:
			(self._modulePath / directory).mkdir(parents=True, exist_ok=True)


	def createFiles(self, files: list):
		for file in files:
			(self._modulePath / file).touch(exist_ok=True)


	def createDestinationFolder(self):
		print('\n----------------------------')
		print('Creating destination folders')

		self.createDirectories([
			'dialogTemplate',
			'talks'
		])

		print('Creating python class')
		self.createTemplateFile(f"{self._general['moduleName']}.py", 'module.py.j2',
			moduleName=self._general['moduleName'],
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

		self.createTemplateFile(f"{self._general['moduleName']}.install", 'install.j2',
			moduleName=self._general['moduleName'],
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
				moduleName=self._general['moduleName'],
				description=self._general['description'],
				username=self._general['username']
			)


	def createTalks(self):
		print('Creating talks')
		for lang in self._general['langs']:
			print(f'- {lang}')
			self.createTemplateFile(f'talks/{lang}.json', 'talks.json.j2')


	def createReadme(self):
		print('Creating readme file')
		self.createTemplateFile('README.md', 'README.md.j2',
			moduleName=self._general['moduleName'],
			description=self._general['description'],
			username=self._general['username'],
			langs=self._general['langs']
		)


	def createWidgets(self):
		moduleWidgets = []
		while True:
			questions = [
				{
					'type'   : 'confirm',
					'name'   : 'widgets',
					'message': 'Are you planning on creating widgets for you module? Widgets are used on the\ninterface to display quick informations that your module can return' if not moduleWidgets else 'Any other widgets?',
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
			moduleWidgets.append(subAnswers['widget'])

		if not moduleWidgets:
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

		self.createFiles([
			'widgets/__init__.py',
			'widgets/css/common.css',
			'widgets/img/.gitkeep',
			'widgets/fonts/.gitkeep'
		])

		for widget in moduleWidgets:
			widget = str(widget).title().replace(' ', '')
			self.createTemplateFile(f'widgets/css/{widget}.css', 'widget.css.j2', widgetName=widget)
			self.createTemplateFile(f'widgets/js/{widget}.js', 'widget.js.j2')
			#(modulePath / 'widgets' / 'lang' / f'{widget}.lang.json').write_text('{}')
			self.createTemplateFile(f'widgets/templates/{widget}.html', 'widget.html.j2', widget=widget)
			self.createTemplateFile(f'widgets/{widget}.py', 'widget.py.j2', widget=widget)


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
		'name'    : 'moduleName',
		'message' : 'Please enter the name of the module you are creating',
		'validate': NotEmpty,
		'filter'  : lambda val: ''.join(x.capitalize() for x in val.split(' '))
	}
]

NEXT_QUESTION = [
	{
		'type'    : 'input',
		'name'    : 'description',
		'message' : 'Please enter a description for this module',
		'validate': NotEmpty,
		'filter'  : lambda val: str(val).capitalize()
	},
	{
		'type'    : 'checkbox',
		'name'    : 'langs',
		'message' : 'Choose the language for this module. Note that to share\nyour module on the official repo english is mandatory',
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
	creates a new module
	"""
	Moduler().start()

