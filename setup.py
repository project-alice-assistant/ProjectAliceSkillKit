import io

from setuptools import find_packages, setup

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

setup(
	name='projectalice-sk',
	author='ProjectAlice',
	version='1.4.0',
	maintainer='Psychokiller1888',
	maintainer_email='laurentchervet@bluewin.ch',
	description='Project Alice skill kit',
	long_description=readme,
	long_description_content_type='text/markdown',
	url='https://github.com/project-alice-assistant/ProjectAliceSkillKit',
	license='GPL-3.0',
	packages=find_packages(),
	include_package_data=True,
	use_scm_version=False,
	setup_requires=['setuptools_scm'],
	install_requires=[
		'jsonschema>=3.0.0',
		'click',
		'unidecode',
		'requests',
		'PyInquirer',
		'prompt_toolkit==1.0.14',
		'jinja2'
	],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3.7",
		"Topic :: Software Development :: Code Generators",
		"Topic :: Software Development :: Testing"
	],
    entry_points='''
        [console_scripts]
        projectalice-sk=ProjectAliceSK.ProjectAliceSkillKit:cli
    '''
)
