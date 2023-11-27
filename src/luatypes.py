from functools import reduce

from fbyte import decode_fbyte
from luainst import InstructKind, LuaInstruct


class LuaError(Exception):
	def __init__(self, msg: str):
		self.msg = msg


def maybe_attempt_op(op_name: str, left, right):
	left_type = type(left)
	right_type = type(right)

	if left_type in NO_ARITHMETIC:
		raise LuaError(f"attempt to perform arithmetic on a {left_type.name} value")
	if right_type in NO_ARITHMETIC:
		raise LuaError(f"attempt to perform arithmetic on a {right_type.name} value")
	if left_type in NO_MATHOPS or right_type in NO_MATHOPS or left_type != right_type:
		raise LuaError(f"attempt to {op_name} a '{left_type.name}' with a '{right_type.name}'")


class LuaObject:
	name: str = "object"
	value: any = None

	def tostring(self): return LuaString(f"{self.name}: 0x{id(self):x}")
	def tonumber(self): return LuaNil()

	def call(self, env, args):
		raise LuaError(f"attempt to call a {self.name} value")

	def get_from(self, key):
		raise LuaError(f"attempt to index a {self.name} value")

	def op_len(self) -> int:
		if type(self) in NO_LENGTH:
			raise LuaError(f"attempt to get length of a {self.name} value")
		return LuaNil()

	def op_add(self, other) -> any:
		maybe_attempt_op("add", self, other)
		return type(self)(self.value + other.value)

	def op_sub(self, other) -> any:
		maybe_attempt_op("sub", self, other)
		return type(self)(self.value - other.value)

	def op_mul(self, other) -> any:
		maybe_attempt_op("mul", self, other)
		return type(self)(self.value * other.value)

	def op_div(self, other) -> any:
		maybe_attempt_op("div", self, other)
		return type(self)(self.value / other.value)

	def op_mod(self, other) -> any:
		maybe_attempt_op("mod", self, other)
		return type(self)(self.value % other.value)

	def op_pow(self, other) -> any:
		maybe_attempt_op("pow", self, other)
		return type(self)(self.value ** other.value)

	def op_unm(self) -> any:
		maybe_attempt_op("unm", self, self)
		return type(self)(-self.value)

	def op_not(self) -> any:
		return LuaBoolean(False)

	def op_concat(self, other) -> any:
		left_type = type(self)
		right_type = type(other)
		if LuaString not in [left_type, right_type]:
			raise LuaError(f"attempt to concat a '{left_type.name}' with a '{right_type.name}'")
		return LuaString(self.tostring().value + other.tostring().value)
	
	def bool(self) -> bool:
		return True

	def __eq__(self, other):
		return type(self) == type(other) and self.value == other.value
	def __ne__(self, other):
		return type(self) == type(other) and self.value != other.value
	def __lt__(self, other):
		return type(self) == type(other) and self.value < other.value
	def __le__(self, other):
		return type(self) == type(other) and self.value <= other.value
	def __gt__(self, other):
		return type(self) == type(other) and self.value > other.value
	def __ge__(self, other):
		return type(self) == type(other) and self.value >= other.value

	def __hash__(self): return hash(self.value)

	def __str__(self): return f"{self.name}: 0x{id(self):x}"
	def __repr__(self): return type(self).__name__ + f"({self.value})"


class LuaNil(LuaObject):
	name = "nil"

	def __init__(self): pass

	def tostring(self): return LuaString("nil")
	def tonumber(self): return self

	def op_not(self, other) -> any: return LuaBoolean(True)
	def bool(self) -> bool: return False

	def __str__(self): return "nil"
	def __repr__(self): return "LuaNil"


class LuaNumber(LuaObject):
	name = "number"

	def __init__(self, value: int | float):
		if isinstance(value, type(self)):
			self.value = value.value
		self.value = float(value)

	def tostring(self):
		if self.value.is_integer():
			return LuaString(str(int(self.value)))
		else:
			return LuaString(str(self.value))

	def tonumber(self):
		return LuaNumber(self.value)

	def __str__(self): return str(self.value)
	def __repr__(self): return f"LuaNumber({self.value})"


class LuaString(LuaObject):
	name = "string"

	def __init__(self, value: str):
		if isinstance(value, type(self)):
			self.value = value.value
		self.value = str(value)

	def tostring(self): return LuaString(self.value)
	def tonumber(self):
		try:
			return LuaNumber(float(self.value))
		except ValueError:
			return LuaNil()
	
	def op_len(self):
		return LuaNumber(len(self.value))

	def __str__(self): return f'"{self.value}"'
	def __repr__(self): return f'LuaString("{self.value}")'


class LuaBoolean(LuaObject):
	name = "boolean"

	def __init__(self, value: bool):
		if isinstance(value, type(self)):
			self.value = value.value
		self.value = bool(value)

	def tostring(self): return LuaString("true") if self.value else LuaString("false")
	def tonumber(self): return LuaNil()

	def bool(self) -> bool: return self.value

	def __str__(self): return "true" if self.value else "false"
	def __repr__(self): return f"LuaBoolean({self.value})"


class LuaTable(LuaObject):
	name = "table"

	def __init__(self, arr_size: int, hash_size: int):
		self.arr_size = arr_size
		self.hash_size = hash_size

		self.arr = [LuaNil()] * arr_size
		self.hash = {}

	def get_from(self, key: LuaString | LuaNumber):
		if key in self.hash.keys():
			return self.hash[key]
		elif isinstance(key, LuaNumber) and 0 <= key.value < len(self.arr):
			return self.arr[int(key.value)]
		else:
			return LuaNil()

	def items(self):
		items = [(LuaNumber(i + 1), v) for i, v in enumerate(self.arr)]
		items.extend(self.hash.items())
		return items

	def keys(self):
		keys = [LuaNumber(i + 1) for i, _ in enumerate(self.arr)]
		keys.extend(self.hash.keys())
		return keys

	def values(self):
		values = self.arr
		values.extend(self.hash.values())
		return values

	def set_hash(self, key: LuaString, val: any):
		self.hash.update({key: val})
	
	def set_arr(self, idx: LuaNumber, val: any):
		if idx.value - 1 == len(self.arr):
			self.arr.append(val)
		else:
			self.arr[int(idx.value - 1)] = val
	
	def set(self, key: LuaString | LuaNumber, val: any):
		if isinstance(key, LuaString) or not key.value.is_integer():
			self.set_hash(key, val)
		else:
			if key.value <= self.op_len().value + 1:
				self.set_arr(key, val)
			else:
				self.set_hash(key, val)

	def op_len(self):
		keys = self.keys()
		arr_keys = list(sorted(k for k in keys if isinstance(k, LuaNumber)))
		i = 0
		for k in arr_keys:
			if k.value < i: continue

			if k.value == i + 1:
				i += 1
			else:
				break
		return LuaNumber(i)
	
	def __repr__(self):
		return f"LuaTable({len(self.keys())})"


class LuaFunction(LuaObject):
	name = "function"

	def __init__(
		self,
		proto_num: int,
		source_name: str,
		first_line_num: int,
		last_line_num: int,
		num_upvals: int,
		num_params: int,
		is_vararg: int,
		max_stack_size: int,
		instructs: list[LuaInstruct],
		consts: list[any],
		func_protos: list[any],
		line_positions: list[int],
		local_vars: list[tuple],
		upval_names: list[str],
		upvals: list[LuaObject] = None
	):
		self.proto_num = proto_num
		self.source_name = source_name
		self.first_line_num = first_line_num
		self.last_line_num = last_line_num
		self.num_upvals = num_upvals
		self.num_params = num_params
		self.is_vararg = is_vararg
		self.max_stack_size = max_stack_size
		self.instructs = instructs
		self.consts = consts
		self.func_protos = func_protos
		self.line_positions = line_positions
		self.local_vars = local_vars
		self.upval_names = upval_names
		self.upvals = upvals or ([None] * num_upvals)

	def closure(self, upvals: list[LuaObject]):
		new_closure = LuaFunction(
			self.proto_num,
			self.source_name,
			self.first_line_num,
			self.last_line_num,
			self.num_upvals,
			self.num_params,
			self.is_vararg,
			self.max_stack_size,
			self.instructs,
			self.consts,
			self.func_protos,
			self.line_positions,
			self.local_vars,
			self.upval_names,
			upvals
		)
		return new_closure

	def set_upval(self, idx: int, val: LuaObject) -> None:
		self.upvals[idx] = val

	def get_upval(self, idx: int) -> LuaObject:
		return self.upvals[idx]

	def get_debug_str(self):
		res = f".function  {self.num_upvals} {self.num_params} x {self.max_stack_size}\n"
		for i, local in enumerate(self.local_vars):
			res += f".local  \"{local[0]}\"  ; {i}\n"
		for i, const in enumerate(self.consts):
			res += f".const  {const}  ; {i}\n"
		for i, upval in enumerate(self.upval_names):
			res += f".upval  \"{upval}\"  ; {i}\n"
		# for i, func in enumerate(self.func_protos):
		# 	res += "\n"
		# 	res += "  " + "\n  ".join(func.get_debug_str().split("\n"))
		# 	res += "\n"
		for i, inst in enumerate(self.instructs):
			pc = f"[{i + 1}]"
			res += f"{pc:>5s} {inst.name:9} "
			match inst.kind:
				case InstructKind.iA:
					res += f"{inst.A:3d}        "
				case InstructKind.iAB:
					res += f"{inst.A:3d} {inst.B:3d}    "
				case InstructKind.iABC:
					res += f"{inst.A:3d} {inst.B:3d} {inst.C:3d}"
				case InstructKind.iABx:
					res += f"{inst.A:3d} {inst.Bx:3d}    "
				case InstructKind.iAC:
					res += f"{inst.A:3d} {inst.C:3d}    "
				case InstructKind.iAsBx:
					res += f"{inst.A:3d} {inst.sBx:3d}    "
				case InstructKind.isBx:
					res += f"{inst.sBx:3d}        "
			res += "\n"
		return res
	
	def __repr__(self):
		return f"LuaFunction([{self.proto_num}], lines {self.first_line_num}:{self.last_line_num})"


class LuaPyFunction(LuaObject):
	name = "function"

	def __init__(self, func: callable):
		self.func = func

	def call(self, env, args):
		res = self.func(*args)
		if isinstance(res, tuple):
			return tuple(make_lua_type(r) for r in res)
		return (make_lua_type(res),)
	
	def __repr__(self):
		return f"LuaPyFunction({self.func.__name__})"


NO_LENGTH = [LuaObject, LuaNil, LuaBoolean, LuaNumber, LuaFunction, LuaPyFunction]
NO_ARITHMETIC = [LuaObject, LuaNil, LuaTable, LuaFunction, LuaPyFunction]
NO_MATHOPS = [LuaBoolean, LuaString]


def make_lua_type(val: any) -> tuple[LuaObject]:
	match val:
		case LuaObject(): return val
		case None: return LuaNil()
		case int(): return LuaNumber(val)
		case float(): return LuaNumber(val)
		case str(): return LuaString(val)
		case dict():
			t = LuaTable(0, len(val))
			for k, v in val.items():
				t.set(make_lua_type(k), make_lua_type(v))
			return t
		case list():
			t = LuaTable(len(val), 0)
			for i, v in enumerate(val):
				t.set(LuaNumber(i + 1), make_lua_type(v))
			return t
		case f if callable(f):
			return LuaPyFunction(f)
		case _:
			raise Exception("unrecognised type: " + str(type(val)))

