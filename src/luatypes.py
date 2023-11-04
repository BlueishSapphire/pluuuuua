from fbyte import decode_fbyte
from luainst import InstructKind, LuaInstruct
from luaenv import LuaEnv


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

	def tostring(self): return f"{self.name}: 0x{id(self):x}"
	def tonumber(self): return LuaNil()

	def call(self):
		raise LuaError(f"attempt to call a {self.name} value")

	def get_from(self):
		raise LuaError(f"attempt to index a {self.name} value")

	def op_len(self) -> int:
		if type(self) in NO_LENGTH:
			raise LuaError(f"attempt to get length of a {self.name} value")

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

	def __str__(self): return f"{self.name}: 0x{id(self):x}"
	def __repr__(self): return type(self).__name__ + f"({self.value})"


class LuaNil(LuaObject):
	name = "nil"

	def __init__(self): pass

	def tostring(self): return self
	def tonumber(self): return self

	def op_not(self, other) -> any: return LuaBoolean(True)

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
	def tonumber(self): return LuaNumber(float(self.value))

	def __str__(self): return self.value
	def __repr__(self): return f"LuaString({self.value})"


class LuaBoolean(LuaObject):
	name = "boolean"

	def __init__(self, value: bool):
		if isinstance(value, type(self)):
			self.value = value.value
		self.value = bool(value)

	def tostring(self): return "true" if self.value else "false"
	def tonumber(self): return LuaNil()

	def __str__(self): return "true" if self.value else "false"
	def __repr__(self): return f"LuaBoolean({self.value})"


class LuaTable(LuaObject):
	name = "table"

	def __init__(self, arr_size: int, hash_size: int):
		self.arr_size = arr_size
		self.hash_size = hash_size

		self.arr = [LuaNil()] * arr_size
		self.hash = {}

	def get_from(self, key: str):
		if isinstance(key, LuaNumber):
			key = key.value
		if isinstance(key, LuaString):
			key = key.value
		return self.hash.get(key, LuaNil())
	def set_hash(self, key: str, val: any): self.hash.update({key: val})
	def set_arr(self, idx: int, val: any): self.arr[idx - 1] = val

	def op_len(self): return len(self.arr) # TODO


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

	def call(self, env, args):
		return call_lua_function(self, env, args)

	def get_debug_str(self):
		res = f".function  {self.num_upvals} {self.num_params} x {self.max_stack_size}\n"
		for i, local in enumerate(self.local_vars):
			res += f".local  \"{local[0]}\"  ; {i}\n"
		for i, const in enumerate(self.consts):
			res += f".const  {const}  ; {i}\n"
		for i, upval in enumerate(self.upval_names):
			res += f".upval  \"{upval}\"  ; {i}\n"
		for i, func in enumerate(self.func_protos):
			res += "\n"
			res += "  " + "\n  ".join(func.get_debug_str().split("\n"))
			res += "\n"
		for i, inst in enumerate(self.instructs):
			res += f"[{i + 1}] {inst.name:9} "
			match inst.kind:
				case InstructKind.iA:
					res += f"{inst.A:3d}"
				case InstructKind.iAB:
					res += f"{inst.A:3d} {inst.B:3d}"
				case InstructKind.iABC:
					res += f"{inst.A:3d} {inst.B:3d} {inst.C:3d}"
				case InstructKind.iABx:
					res += f"{inst.A:3d} {inst.Bx:3d}"
				case InstructKind.iAC:
					res += f"{inst.A:3d} {inst.C:3d}"
				case InstructKind.iAsBx:
					res += f"{inst.A:3d} {inst.sBx:3d}"
				case InstructKind.isBx:
					res += f"{inst.sBx:3d}"
			res += "\n"
		return res


class LuaPyFunction(LuaObject):
	name = "function"

	def __init__(self, func: callable):
		self.func = func

	def call(self, env, args):
		res = self.func(*args)
		if isinstance(res, tuple):
			return tuple(make_lua_type(r) for r in res)
		return (make_lua_type(res),)


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
				t.set_hash(k, make_lua_type(v))
			return t
		case list():
			t = LuaTable(len(val), 0)
			for i, v in enumerate(val):
				t.set_arr(i + 1, make_lua_type(v))
			return t
		case _:
			raise Exception("unrecognised type: " + str(type(val)))


class LuaStack:
	def __init__(self, max_stack_size: int):
		self.max_stack_size = max_stack_size
		self.registers = [None] * max_stack_size
		self.pool = {}

	def __getitem__(self, idx: int):
		return self.registers[idx]

	def __setitem__(self, idx: int, val: LuaObject):
		# assert isinstance(val, LuaObject), "tried to set a non-lua value to a register"
		self.registers[idx] = val

	def __len__(self):
		return len(self.registers)

	def open_upval(self, idx: int):
		self.pool.update({idx: self[idx]})
		return LuaUpvalue(self, idx)

	def get_upval(self, idx: int) -> LuaObject:
		return self.pool[idx]

	def set_upval(self, idx: int, val: LuaObject):
		assert isinstance(val, LuaObject), "tried to set a non-lua value to an upvalue"
		self.pool[idx] = val

	def close_upval(self, idx: int):
		self.registers.pop(idx)
		self.registers.append(None)


class LuaUpvalue(LuaObject):
	def __init__(self, parent: LuaStack, idx: int):
		self.parent = parent
		self.idx = idx

	def set(self, val: LuaObject):
		self.parent.set_upval(self.idx, val)

	def get(self):
		return self.parent.get_upval(self.idx)

	def close(self):
		self.parent.close_upval(self.idx)


def call_lua_function(lua_func, env: LuaEnv, args: list[LuaObject]):
	pc = 0
	stack = LuaStack(lua_func.max_stack_size)
	const = lua_func.consts
	upval = lua_func.upvals

	def stack_or_const(val: int):
		return const[val ^ 256] if val & 256 else stack[val]

	while pc < len(lua_func.instructs):
		inst = lua_func.instructs[pc]
		A, B, C, Bx, sBx = inst.A, inst.B, inst.C, inst.Bx, inst.sBx

		# input(f"{lua_func.proto_num}:[{pc + 1}] {inst.name}")

		match inst.opcode:
			case 0x00: # move
				stack[A] = stack[B]
			case 0x01: # loadk
				stack[A] = const[Bx]
			case 0x02: # loadbool
				stack[A] = LuaBoolean(B)
				if bool(C):
					pc += 1
			case 0x03: # loadnil
				for i in range(A, B + 1):
					stack[i] = LuaNil()
			case 0x04: # getupval
				stack[A] = upval[B].get()
			case 0x05: # getglobal
				stack[A] = env.get(const[Bx])
			case 0x06: # gettable
				stack[A] = stack[B].get_from(stack_or_const(C))
			case 0x07: # setglobal
				env.set(const[Bx], stack[A])
			case 0x08: # setupval
				upval[B].set(stack[A])
			case 0x09: # settable
				stack[A].set_hash(stack_or_const(B), stack_or_const(C))
			case 0x0A: # newtable
				stack[A] = LuaTable(decode_fbyte(B), decode_fbyte(C))
			case 0x0B: # self
				stack[A + 1] = stack[B]
				stack[A] = stack[B].get_from(stack_or_const(C))
			case 0x0C: # add
				stack[A] = stack_or_const(B).op_add(stack_or_const(C))
			case 0x0D: # sub
				stack[A] = stack_or_const(B).op_sub(stack_or_const(C))
			case 0x0E: # mul
				stack[A] = stack_or_const(B).op_mul(stack_or_const(C))
			case 0x0F: # div
				stack[A] = stack_or_const(B).op_div(stack_or_const(C))
			case 0x10: # mod
				stack[A] = stack_or_const(B).op_mod(stack_or_const(C))
			case 0x11: # pow
				stack[A] = stack_or_const(B).op_pow(stack_or_const(C))
			case 0x12: # unm
				stack[A] = stack[B].op_unm()
			case 0x13: # not
				stack[A] = stack[B].op_not()
			case 0x14: # len
				stack[A] = stack[B].op_len()
			case 0x15: # concat
				stack[A] = LuaString("".join(map(lambda s: s.value, stack[B:C + 1])))
			case 0x16: # jmp
				pc += sBx
			case 0x17: # eq
				if (stack_or_const(B) == stack_or_const(C)) != bool(A):
					pc += 1
			case 0x18: # lt
				if (stack_or_const(B) < stack_or_const(C)) != bool(A):
					pc += 1
			case 0x19: # le
				if (stack_or_const(B) <= stack_or_const(C)) != bool(A):
					pc += 1
			case 0x1A: # test
				if bool(stack[B]) == bool(C):
					pc += 1
			case 0x1B: # testset
				if bool(stack[B]) == bool(C):
					pc += 1
				else:
					stack[A] = stack[B]
			case 0x1C: # call
				if B == 1:
					res = stack[A].call(env, [])
				elif B == 0:
					res = stack[A].call(env, stack[A + 1:])
				else:
					res = stack[A].call(env, stack[A + 1:A + B])

				num_res = (C - 1) if C >= 1 else len(res)
				# print(f"call: returned with {num_res} results {res}")

				for i in range(num_res):
					stack[A + i] = res[i]
			case 0x1D: # tail_call
				if B == 1:
					res = stack[A].call(env, [])
				elif B == 0:
					res = stack[A].call(env, stack[A + 1:])
				else:
					res = stack[A].call(env, stack[A + 1:A + B])

				# print(f"tailcall: returning with {len(res)} results {res}")
				return res
			case 0x1E: # returns
				if B == 1:
					res = (LuaNil(),)
				elif B == 0:
					if len(stack[A:]) == 1:
						res = (stack[A],)
					else:
						res = tuple(stack[A:])
				else:
					res = tuple(stack[A:A + B - 1])
				# print(f"return: returning with {len(res)} results {res}")
				for i in range(A, len(stack)):
					stack.close_upval(i)
				return res
			case 0x1F: # forloop
				stack[A] += stack[A + 2]
				if stack[A] <= stack[A + 1]:
					pc += sBx
					stack[A + 3] = stack[A]
			case 0x20: # forprep
				stack[A] -= stack[A + 2]
				pc += sBx
			case 0x21: # tforloop
				res = stack[A].call(env, [], [stack[A + 1], stack[A + 2]])
				for i in range(0, C):
					stack[A + i + 3] = res[i]

				if isinstance(stack[A + 3], LuaNil):
					stack[A + 2] = stack[A + 3]
				else:
					pc += 1
			case 0x22: # setlist
				LFIELDS_PER_FLUSH = 50

				if B == 0:
					B = len(stack) - A
				if C == 0:
					pc += 1
					next_inst = lua_func.instructs[pc].raw
					C = next_inst[0] << 24 | next_inst[1] << 16 | next_inst[2] << 8 | next_inst[3]

				for i in range(1, B + 1):
					stack[A].set_arr(
						((C - 1) * LFIELDS_PER_FLUSH + i),
						stack[A + i]
					)
			case 0x23: # close
				# TODO
				for v in stack[A:]:
					stack.close_upval(v)
			case 0x24: # closure
				func = lua_func.func_protos[Bx]
				new_upvals = []
				while lua_func.instructs[pc + 1].opcode in {0x00, 0x04}:
					pc += 1
					inst = lua_func.instructs[pc]

					# input(f" -> {inst.name}")

					match inst.opcode:
						case 0x00: # move
							new_upvals.append(stack.open_upval(inst.B))
						case 0x04: # getupval
							new_upvals.append(upval[inst.B])

				if len(new_upvals) != func.num_upvals:
					raise Exception("Internal VM error")

				stack[A] = func.closure(new_upvals)
			case 0x25: # vararg
				raise LuaError("Not implemented: vararg") # TODO

		pc += 1
