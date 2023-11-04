class LuaEnv:
	def __init__(self):
		self.globals = {}

	def get(self, name):
		from luatypes import LuaNil
		return self.globals.get(name.value, LuaNil())

	def set(self, name, val):
		self.globals[name.value] = val

	def get_default():
		# avoid circular import
		from luatypes import LuaPyFunction, make_lua_type

		env = LuaEnv()
		env.globals = {
			"print": LuaPyFunction(lambda *args: print(*[a.tostring() for a in args])),
			"tostring": LuaPyFunction(lambda o: o.tostring()),
			"tonumber": LuaPyFunction(lambda o: o.tonumber()),
			"string": make_lua_type({
				"bytes": LuaPyFunction(lambda: None),
				"char": LuaPyFunction(lambda: None),
				"dump": LuaPyFunction(lambda: None),
				"find": LuaPyFunction(lambda: None),
				"format": LuaPyFunction(lambda: None),
				"gmatch": LuaPyFunction(lambda: None),
				"gsub": LuaPyFunction(lambda: None),
				"len": LuaPyFunction(lambda s: len(s.value)),
				"lower": LuaPyFunction(lambda s: s.value.lower()),
				"match": LuaPyFunction(lambda: None),
				"pack": LuaPyFunction(lambda: None),
				"packsize": LuaPyFunction(lambda: None),
				"rep": LuaPyFunction(lambda: None),
				"reverse": LuaPyFunction(lambda s: s.value[::-1]),
				"sub": LuaPyFunction(lambda s, i, j=None: s.value[int(i.value):int(j.value)] if j else s.value[int(i.value):]),
				"unpack": LuaPyFunction(lambda: None),
				"upper": LuaPyFunction(lambda s: s.value.upper()),
			}),
		}
		return env
