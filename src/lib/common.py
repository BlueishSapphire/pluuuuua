def optional_arg(funcname, args, idx, kind = None):
	from luatypes import LuaNil
	if idx - 1 >= len(args) or isinstance(args[idx - 1], LuaNil): return

	arg = args[idx - 1]
	if kind is not None and arg.name != kind:
		from luatypes import LuaError
		raise LuaError(f"bad argument #{idx} to '{funcname}' ({kind} expected, got {arg.name})")


def required_arg(funcname, args, idx, kind = None):
	if idx - 1 >= len(args) or args[idx - 1] is None:
		from luatypes import LuaError
		raise LuaError(f"bad argument #{idx} to '{funcname}' (value expected)")
	
	arg = args[idx - 1]
	if kind is not None and arg.name != kind:
		from luatypes import LuaError
		raise LuaError(f"bad argument #{idx} to '{funcname}' ({kind} expected, got {arg.name})")


def all_args(funcname, args, kind):
	for i in range(len(args)):
		required_arg(funcname, args, i + 1, kind)