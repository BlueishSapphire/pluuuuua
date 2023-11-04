class LuaEnv:
	def __init__(self):
		self.globals = {}

	def get(self, name):
		from luatypes import LuaNil
		return self.globals.get(name.value, LuaNil())

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
