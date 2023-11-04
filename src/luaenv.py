from luatypes import *

from functools import partial


class LuaEnv:
	def __init__(self):
		self.globals = {}
		self.func_protos = []

	def new_func(self, func):
		len_diff = func.proto_num - len(self.func_protos)
		
		if len_diff >= 0:
			self.func_protos.extend([None] * (len_diff + 1))
		
		self.func_protos[func.proto_num] = func

	def get_func(self, proto_num):
		return self.func_protos[proto_num]

	def get(self, name):
		return self.globals.get(name.value, LuaNil)
	
	def set(self, name, val):
		self.globals[name.value] = val

	def get_default():
		def lua_print(*args):
			print("lua_print", *args)
		
		def lua_tostring(arg):
			res = arg.tostring()
			print("lua_tostring", arg, "->", res)
			return res
		
		def lua_tonumber(arg):
			res = arg.tonumber()
			print("lua_tonumber", arg, "->", res)
			return res

		from luatypes import LuaPyFunction

		env = LuaEnv()
		env.globals = {
			"print": LuaPyFunction(lua_print),
			"tostring": LuaPyFunction(lua_tostring),
			"tonumber": LuaPyFunction(lua_tonumber),
		}
		return env
