def optional_arg(funcname, args, idx, *kinds):
	from luatypes import LuaNil
	if idx - 1 >= len(args) or isinstance(args[idx - 1], LuaNil): return

	arg = args[idx - 1]
	if len(kinds) > 0 and arg.name not in kinds:
		from luatypes import LuaError
		raise LuaError(f"bad argument #{idx} to '{funcname}' ({kinds[0]} expected, got {arg.name})")


def required_arg(funcname, args, idx, *kinds):
	if idx - 1 >= len(args) or args[idx - 1] is None:
		from luatypes import LuaError
		raise LuaError(f"bad argument #{idx} to '{funcname}' (value expected)")
	
	arg = args[idx - 1]
	if len(kinds) > 0 and arg.name not in kinds:
		from luatypes import LuaError
		raise LuaError(f"bad argument #{idx} to '{funcname}' ({kinds[0]} expected, got {arg.name})")


def all_args(funcname, args, *kinds):
	for i in range(len(args)):
		required_arg(funcname, args, i + 1, *kinds)