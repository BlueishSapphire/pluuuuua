from lib.common import *


def byte(*args):
	required_arg("byte", args, 1, "string")
	optional_arg("byte", args, 2, "number")
	idx = args[1].value if len(args) > 1 else 0
	return ord(args[0].value[idx])

def char(*args):
	all_args("char", args, "number")
	return "".join(chr(n) for n in args)

def dump(*args):
	required_arg("dump", args, 1, "function")
	return None

def find(*args):
	required_arg("find", args, 1, "string")
	required_arg("find", args, 2, "string")
	idx = args[0].value.find(args[1].value)
	if idx == -1:
		from luatypes import LuaNil
		return LuaNil()
	return (idx, idx + len(args[1].value))

_format = format
def format(*args):
	return None

def gfind(*args):
	return None

def gmatch(*args):
	return None

def gsub(*args):
	return None

_len = len
def len(*args):
	required_arg("len", args, 1, "string")
	return _len(args[0].value)

def lower(*args):
	required_arg("lower", args, 1, "string")
	return args[0].lower()

def match(*args):
	return None

def rep(*args):
	required_arg("rep", args, 1, "string")
	required_arg("rep", args, 2, "number")
	return args[0].value * args[1].value

def reverse(*args):
	required_arg("reverse", args, 1, "string")
	return args[0].value[::-1]

def sub(*args):
	required_arg("sub", args, 1, "string")
	required_arg("sub", args, 2, "number")
	optional_arg("sub", args, 3, "number")
	start = args[1].value
	if len(args) > 2:
		end = args[2].value
		return args[0].value[start:end + 1]
	else:
		return args[0].value[start:]

def upper(*args):
	required_arg("upper", args, 1, "string")
	return args[0].upper()

lua_strlib = {
	"bytes": bytes,
	"char": char,
	"dump": dump,
	"find": find,
	"format": format,
	"gmatch": gmatch,
	"gsub": gsub,
	"len": len,
	"lower": lower,
	"match": match,
	"rep": rep,
	"reverse": reverse,
	"sub": sub,
	"upper": upper,
}
