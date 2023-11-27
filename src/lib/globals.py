from lib.common import *
import subprocess
import os.path


def lua_print(*args):
	print(*[a.tostring().value for a in args], sep="\t")

def lua_error(*args):
	optional_arg("error", args, 1)
	optional_arg("error", args, 2)
	from luatypes import LuaError
	if len(args) == 0:
		raise LuaError()
	elif len(args) == 1:
		raise LuaError(args[0].value)
	else:
		raise LuaError(args[0].value)

def lua_assert(*args):
	required_arg("assert", args, 1)
	optional_arg("assert", args, 2)
	if not args[0].bool():
		from luatypes import LuaError
		if len(args) > 1:
			raise LuaError(args[1].value)
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

def lua_dofile(*args):
	required_arg("dofile", args, 1, "string")
	filename = args[0].value
	if not os.path.exists(filename):
		from luatypes import LuaError
		raise LuaError(f"cannot open {filename}: No such file or directory")

	proc = subprocess.Popen(args=["luac5.1", "-o", "/dev/stdout", filename], stdout=subprocess.PIPE)
	bytecode = proc.stdout.read()
	from luafile import LuaFile
	luafile = LuaFile(filename, bytecode)
	return luafile.execute()

def lua_dostring(*args):
	required_arg("dostring", args, 1, "string")
	proc = subprocess.Popen(args=["luac5.1", "-o", "/dev/stdout", "-"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	bytecode = proc.communicate(input=args[0].value.encode())[0]
	from luafile import LuaFile
	luafile = LuaFile(":string", bytecode)
	return luafile.execute()

def lua_require(*args):
	# TODO don't reload already loaded files
	required_arg("dofile", args, 1, "string")
	if not os.path.exists(args[0]):
		from luatypes import LuaError
		raise LuaError(f"cannot open {args[0]}: No such file or directory")

	proc = subprocess.Popen(args=["luac5.1", "-o", "/dev/stdout", args[0]], stdout=subprocess.PIPE)
	bytecode = proc.stdout.read()
	luafile = LuaFile(args[0], bytecode)
	return luafile.execute()

def lua_setglobal(*args):
	pass

def lua_getglobal(*args):
	pass

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
	"dofile": lua_dofile,
	"dostring": lua_dostring,
	"require": lua_require,
	"setglobal": lua_setglobal,
	"getglobal": lua_getglobal,
}
