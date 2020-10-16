import os
import subprocess
import sys
from pathlib import Path

import click


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
	process: subprocess.CompletedProcess = subprocess.run([str(path), '--cov=./', '--cov-report=xml'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	ret = 0 if not process.returncode else process.returncode
	sys.exit(ret)


if __name__ == '__main__':
	unittests()
