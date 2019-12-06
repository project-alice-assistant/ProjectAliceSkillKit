import io

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

setup(
	name='alice-sk',
	author='ProjectAlice',
    maintainer='Max Bachmann',
    maintainer_email='kontakt@maxbachmann.de',
    description='skill kit of project alice',
	long_description=readme,
    long_description_content_type='text/markdown',
	url='https://github.com/project-alice-powered-by-snips/ProjectAliceSkillKit',
	license='GPL-3.0',
    packages=find_packages(),
    include_package_data=True,
	use_scm_version=True,
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
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points='''
        [console_scripts]
        alice-sk=AliceSK.ProjectAliceSkillKit:cli
    '''
)