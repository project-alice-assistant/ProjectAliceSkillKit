#  Copyright (c) 2021
#
#  This file, Helpers.py, is part of Project Alice.
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
#  Last modified: 2021.07.28 at 16:34:11 CEST

import click


class OptionEatAll(click.Option):
	"""
	taken from https://stackoverflow.com/questions/48391777/nargs-equivalent-for-options-in-click
	"""


	def __init__(self, *args, **kwargs):
		self.save_other_options = kwargs.pop('save_other_options', True)
		nargs = kwargs.pop('nargs', -1)
		assert nargs == -1, f'nargs, if set, must be -1 not {nargs}'
		super(OptionEatAll, self).__init__(*args, **kwargs)
		self._previous_parser_process = None
		self._eat_all_parser = None


	def add_to_parser(self, parser, ctx):

		def parser_process(value, state):
			# method to hook to the parser.process
			done = False
			value = [value]
			if self.save_other_options:
				# grab everything up to the next option
				while state.rargs and not done:
					for prefix in self._eat_all_parser.prefixes:
						if state.rargs[0].startswith(prefix):
							done = True
					if not done:
						value.append(state.rargs.pop(0))
			else:
				# grab everything remaining
				value += state.rargs
				state.rargs[:] = []
			value = tuple(value)

			# call the actual process
			self._previous_parser_process(value, state)


		retval = super(OptionEatAll, self).add_to_parser(parser, ctx)
		for name in self.opts:
			# noinspection PyProtectedMember
			our_parser = parser._long_opt.get(name) or parser._short_opt.get(name)
			if our_parser:
				self._eat_all_parser = our_parser
				self._previous_parser_process = our_parser.process
				our_parser.process = parser_process
				break
		return retval
