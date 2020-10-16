import os
import sys
from pathlib import Path

import click
import pytest


@click.command()
@click.option('-s', '--skill', default=None, type=str, help='The skill to run tests on')
def unittests(skill: str):
	if not skill:
		skill = os.getcwd()

	skillPath = Path(skill)
	path = skillPath / 'tests'
	if not path.exists():
		print('No unittests found, aborting')
		sys.exit(0)

	print('Found tests to be run, starting')
	result = pytest.main([str(path), '--cov=./', '--cov-report=xml'])
	sys.exit(result)


if __name__ == '__main__':
	unittests()
