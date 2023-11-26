def lua_print(*args):
	print(*[a.tostring() for a in args])

def lua_error(msg = None, code = None):
	from luatypes import LuaError
	raise LuaError(msg)

def lua_type(o):
	return o.name

def lua_tostring(o):
	return o.tostring()

def lua_tonumber(o):
	return o.tonumber()

lua_globals = {
	"print": lua_print,
	"error": lua_error,
	"type": lua_type,
	"tostring": lua_tostring,
	"tonumber": lua_tonumber,
}
