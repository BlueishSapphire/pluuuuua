from lib.common import *
from luatypes import *


def tab_insert(*args):
	required_arg("insert", args, 1, "table")
	required_arg("insert", args, 2)
	optional_arg("insert", args, 3)

	t = args[0]

	if len(args) == 2:
		t.arr.append(args[1])
	else:
		i = int(args[1].value) - 1
		v = args[2]
		t.arr = t.arr[:i] + [v] + t.arr[i:]


def tab_concat(*args):
	required_arg("concat", args, 1, "table")
	optional_arg("concat", args, 2, "string")
	optional_arg("concat", args, 3, "number")
	optional_arg("concat", args, 4, "number")
	
	t = args[0]
	sep = args[1] if len(args) > 1 else ""
	i = (args[2] - 1) if len(args) > 2 else 0
	j = args[3] if len(args) > 3 else len(t.arr)

	for idx, value in enumerate(t.arr[i:j + 1]):
		if value.name not in {"string", "number"}:
			raise LuaError(f"invalid value ({value.name}) at index {idx + 1} in table for 'concat'")

	# print(i, j, t.arr)
	return sep.join([e.tostring().value for e in t.arr[i:j]])


def tab_sort(*args):
	required_arg("sort", args, 1, "table")
	optional_arg("sort", args, 2, "function")
	# TODO


def tab_remove(*args):
	required_arg("remove", args, 1, "table")
	optional_arg("remove", args, 2, "string", "number")
	# TODO


def tab_foreach(*args):
	required_arg("foreach", args, 1, "table")
	required_arg("foreach", args, 2, "function")
	# TODO


def tab_foreachi(*args):
	required_arg("foreachi", args, 1, "table")
	required_arg("foreachi", args, 2, "function")
	# TODO


def tab_setn(*args):
	raise LuaError("'setn' is obsolete")


def tab_getn(*args):
	required_arg("getn", args, 1, "table")
	keys = args[0].keys()
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