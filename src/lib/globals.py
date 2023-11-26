from lib.common import *


def lua_print(*args):
	print(*[a.tostring() for a in args], sep="\t")

def lua_error(*args):
	optional_arg("error", args, 1)
	optional_arg("error", args, 2)
	from luatypes import LuaError
	if len(args) == 0:
		raise LuaError()
	elif len(args) == 1:
		raise LuaError(args[0])
	else:
		raise LuaError(args[0])

def lua_assert(*args):
	required_arg("assert", args, 1)
	optional_arg("assert", args, 2)
	if args[0].op_not():
		if len(args) > 1:
			raise LuaError(args[1])
		else:
			raise LuaError("assertion failed!")

def lua_type(*args):
	required_arg("type", args, 1)
	return args[0].name

def lua_tostring(*args):
	required_arg("tostring", args, 1)
	return args[0].tostring()

def lua_tonumber(*args):
	required_arg("tonumber", args, 1)
	return args[0].tonumber()

def lua_next(*args):
	required_arg("next", args, 1, "table")
	required_arg("next", args, 2, "nil", "string", "number")
	from luatypes import LuaNil
	if isinstance(args[1], LuaNil):
		idx = 1
	else:
		idx = args[0].keys().index(args[1]) + 2
	items = args[0].items()
	return items[idx - 1] if idx <= len(items) else (None, None)

def lua_pairs(*args):
	required_arg("pairs", args, 1, "table")
	return lua_next, args[0], None

def lua_ipairs(*args):
	required_arg("ipairs", args, 1, "table")
	return # TODO

lua_globals = {
	"print": lua_print,
	"error": lua_error,
	"assert": lua_assert,
	"type": lua_type,
	"tostring": lua_tostring,
	"tonumber": lua_tonumber,
	"next": lua_next,
	"pairs": lua_pairs,
	"ipairs": lua_ipairs,
}
