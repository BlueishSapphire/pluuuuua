from lib.common import *


def tab_insert(*args):
	required_arg("insert", args, 1, "table")
	required_arg("insert", args, 2)
	optional_arg("insert", args, 3)

	if len(args) == 2:
		args[0].arr.append(args[1])
	else:
		args[0].set_hash(args[1], args[2])


def tab_concat(*args):
	required_arg("concat", args, 1, "table")
	required_arg("concat", args, 2, "string")
	required_arg("concat", args, 3, "number")
	required_arg("concat", args, 4, "number")
	# table, sep, i, j


def tab_sort(*args):
	required_arg("sort", args, 1, "table")
	optional_arg("sort", args, 2, "function")


def tab_remove(*args):
	required_arg("remove", args, 1, "table")
	optional_arg("remove", args, 2, "string", "number")


def tab_foreach(*args):
	required_arg("foreach", args, 1, "table")
	required_arg("foreach", args, 2, "function")


def tab_foreachi(*args):
	required_arg("foreachi", args, 1, "table")
	required_arg("foreachi", args, 2, "function")


def tab_setn(*args):
	from luatypes import LuaError
	raise LuaError("'setn' is obsolete")


def tab_getn(*args):
	required_arg("getn", args, 1, "table")
	keys = args[0].keys()
	from luatypes import LuaNumber
	for i in range(1, len(keys) + 1):
		if LuaNumber(i) not in keys:
			break
	return i - 1


def tab_maxn(*args):
	required_arg("maxn", args, 1, "table")
	return max(args[0].hash.keys())


lua_tablib = {
	"insert": tab_insert,
	"concat": tab_concat,
	"sort": tab_sort,
	"remove": tab_remove,
	"foreach": tab_foreach,
	"foreachi": tab_foreachi,
	"setn": tab_setn,
	"getn": tab_getn,
	"maxn": tab_maxn,
}