from lib.globals import lua_globals
from lib.math import lua_mathlib
from lib.string import lua_strlib
from lib.table import lua_tablib

from luatypes import *


def lua_io_read(what: str | None = None) -> str:
	res = input()
	if what and what.startswith("*n"):
		res = float(res)
	return res


class LuaEnv:
	def __init__(self):
		self.globals = {}

	def get(self, name):
		return self.globals.get(name.value, LuaNil())

	def set(self, name, val):
		self.globals[name.value] = val

	def get_default():
		# avoid circular import

		env = LuaEnv()
		env.globals = {}
		env.globals.update({k: make_lua_type(v) for k, v in lua_globals.items()})
		env.globals.update({ "math": make_lua_type(lua_mathlib) })
		env.globals.update({ "string": make_lua_type(lua_strlib) })
		env.globals.update({ "table": make_lua_type(lua_tablib) })
		return env
