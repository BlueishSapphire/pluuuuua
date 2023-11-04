from luainst import *


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
	
	def tostring(self) -> any: return LuaNil()
	def tonumber(self) -> any: return LuaNil()

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

	def __init__(self, value: int | float): self.value = float(value)
	def tostring(self): return LuaString(str(self.value))
	def tonumber(self): return self
	
	def __str__(self): return str(self.value)
	def __repr__(self): return f"LuaNumber({self.value})"


class LuaString(LuaObject):
	name = "string"

	def __init__(self, value: str): self.value = str(value)
	def tostring(self): return self
	def tonumber(self): return LuaNumber(str(self.value))
	
	def __str__(self): return self.value
	def __repr__(self): return f"LuaString({self.value})"


class LuaBoolean(LuaObject):
	name = "boolean"

	def __init__(self, value: bool): self.value = bool(value)
	def tostring(self): return "true" if self.value else "false"
	def tonumber(self): return LuaNil

	def __str__(self): return "true" if self.value else "false"
	def __repr__(self): return f"LuaBoolean({self.value})"


class LuaTable(LuaObject):
	name = "table"

	def __init__(self, arr_size: int, hash_size: int):
		self.arr_size = arr_size
		self.hash_size = hash_size

		self.arr = [LuaNil] * arr_size
		self.hash = {}
	def tostring(self): return f"table: 0x{id(self):X}"
	def tonumber(self): return LuaNil()
	def get_from(self, key: str): return self.hash.get(key, lua_Nil)
	def set_hash(self, key: str, val: any): self.hash.update({key: val})
	def set_arr(self, idx: int, val: any): self.arr[idx - 1] = val
	
	def op_len(self): return len(self.arr) # TODO

	def __str__(self): return f"table: 0x{id(self):X}"
	def __repr__(self): return f"LuaTable({self.value})"


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
		all_locals: list[tuple],
		all_upvals: list[str],
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
		self.all_locals = all_locals
		self.all_upvals = all_upvals

	def tostring(self): return f"function: 0x{id(self):X}"
	def tonumber(self): return LuaNil()

	def call(self, env, upvals, args):
		return call_lua_function(self, env, upvals, args)

	def __str__(self): return f"function: 0x{id(self):X}"
	def __repr__(self): return f"LuaFunction({self.value})"


class LuaPyFunction(LuaObject):
	name = "py function"

	def __init__(self, func: callable):
		self.func = func

	def call(self, env, upvals, args):
		res = self.func(*args)
		return make_lua_type(res)
	
	def __str__(self): return self.func.__name__
	def __repr__(self): return f"LuaPyFunction({self.func.__name__})"


NO_LENGTH = [LuaObject, LuaNil, LuaBoolean, LuaNumber, LuaFunction, LuaPyFunction]
NO_ARITHMETIC = [LuaObject, LuaNil, LuaTable, LuaFunction, LuaPyFunction]
NO_MATHOPS = [LuaBoolean, LuaString]


def make_lua_type(val: any) -> tuple[LuaObject]:
	match val:
		case LuaObject(): return (val,)
		case None: return (LuaNil(),)
		case int(): return (LuaNumber(val),)
		case float(): return (LuaNumber(val),)
		case str(): return (LuaString(val),)
		case dict():
			t = LuaTable(0, len(val))
			for k, v in val.items():
				t.set_hash(k, make_lua_type(v))
			return (t,)
		case list():
			t = LuaTable(len(val), 0)
			for i, v in enumerate(val):
				t.set_arr(i + 1, make_lua_type(v))
			return (t,)
		case tuple():
			return tuple(make_lua_type(v) for v in val)
		case _:
			raise Exception("unrecognised type: " + str(type(val)))


def call_lua_function(lua_func, env: LuaEnv, upvals: list[LuaObject], args: list[LuaObject]):
	pc = 0
	reg = [LuaNil] * lua_func.max_stack_size
	const = lua_func.consts
	upval = [None] * lua_func.num_upvals

	def reg_or_const(val: int):
		return const[val ^ 256] if val & 256 else reg[val]

	while pc < len(lua_func.instructs):
		inst = lua_func.instructs[pc]
		A, B, C, Bx, sBx = inst.A, inst.B, inst.C, inst.Bx, inst.sBx
		
		match inst.opcode:
			case 0x00: # move
				reg[A] = reg[B]
			case 0x01: # loadk
				reg[A] = const[Bx]
			case 0x02: # loadbool
				reg[A] = LuaBool(reg[B])
				if bool(C): pc += 1
			case 0x03: # loadnil
				for i in range(A, B + 1):
					reg[i] = LuaNil()
			case 0x04: # getupval
				reg[A] = upval[B]
			case 0x05: # getglobal
				reg[A] = env.get(const[Bx])
			case 0x06: # gettable
				reg[A] = reg[B].get(reg_or_const(C))
			case 0x07: # setglobal
				env.set(const[Bx], reg[A])
			case 0x08: # setupval
				upval[B] = reg[A]
			case 0x09: # settable
				reg[A].set_hash(reg_or_const(B), reg_or_const(C))
			case 0x0A: # newtable
				reg[A] = lua_Table(decode_fbyte(B), decode_fbyte(C))
			case 0x0B: # self
				reg[A + 1] = reg[B]
				reg[A] = reg[B].get(reg_or_const(C))
			case 0x0C: # add
				reg[A] = reg_or_const(B).op_add(reg_or_const(C))
			case 0x0D: # sub
				reg[A] = reg_or_const(B).op_sub(reg_or_const(C))
			case 0x0E: # mul
				reg[A] = reg_or_const(B).op_mul(reg_or_const(C))
			case 0x0F: # div
				reg[A] = reg_or_const(B).op_div(reg_or_const(C))
			case 0x10: # mod
				reg[A] = reg_or_const(B).op_mod(reg_or_const(C))
			case 0x11: # pow
				reg[A] = reg_or_const(B).op_pow(reg_or_const(C))
			case 0x12: # unm
				reg[A] = reg[B].op_unm()
			case 0x13: # not
				reg[A] = reg[B].op_not()
			case 0x14: # len
				reg[A] = reg[B].op_len()
			case 0x15: # concat
				reg[A] = LuaString("".join(map(lambda s: s.value, reg[B:C+1])))
			case 0x16: # jmp
				pc += sBx
			case 0x17: # eq
				if (RK(B) == RK(C)) != bool(A):
					pc += 1
			case 0x18: # lt
				if (RK(B) < RK(C)) != bool(A):
					pc += 1
			case 0x19: # le
				if (RK(B) <= RK(C)) != bool(A):
					pc += 1
			case 0x1A: # test
				if bool(reg[B]) == bool(C):
					pc += 1
			case 0x1B: # testset
				if bool(reg[B]) == bool(C):
					pc += 1
				else:
					reg[A] = reg[B]
			case 0x1C: # call
				print("stack", reg)
				if B == 1:
					print(f"calling nargs=0")
					res = reg[A].call(env, [], [])
				elif B == 0:
					print(f"calling nargs=(var){len(reg[A+1:])}")
					res = reg[A].call(env, [], reg[A+1:])
				else:
					print(f"calling nargs={B - 1}")
					res = reg[A].call(env, [], reg[A+1:A+B])

				num_res = (C - 1) if C >= 1 else len(res)
				print(f"result nres={num_res} res={res}")
				print("stack", reg)

				for i in range(num_res):
					reg[A + i] = res[i]
			case 0x1D: # tail_call
				if B == 1:
					res = reg[A].call(env, [], [])
				elif B == 0:
					res = reg[A].call(env, [], reg[A+1:])
				else:
					res = reg[A].call(env, [], reg[A+1:A+B])
				
				return res
			case 0x1E: # return
				# TODO close upvalues

				if B == 1:
					return (LuaNil(),)
				elif B == 0:
					if len(reg[A:]) == 1:
						return (reg[A],)
					else:
						return tuple(reg[A:])
				else:
					return tuple(reg[A:A+B-1])
			case 0x1F: # forloop
				reg[A] += reg[A + 2]
				if reg[A] <= reg[A + 1]:
					pc += sBx
					reg[A + 3] = reg[A]
			case 0x20: # forprep
				reg[A] -= reg[A + 2]
				pc += sBx
			case 0x21: # tforloop
				res = reg[A].call(env, [], [reg[A + 1], reg[A + 2]])
				for i in range(0, C):
					reg[A + i + 3] = res[i]
				
				if isinstance(reg[A + 3], LuaNil):
					reg[A + 2] = reg[A + 3]
				else:
					pc += 1
			case 0x22: # setlist
				LFIELDS_PER_FLUSH = 50

				if B == 0:
					B = len(reg) - A
				if C == 0:
					pc += 1
					next_inst = lua_func.instructs[pc].raw
					C = next_inst[0] << 24 | next_inst[1] << 16 | next_inst[2] << 8 | next_inst[3]
				
				for i in range(1, B + 1):
					reg[A].set_arr(
						((C - 1) * LFIELDS_PER_FLUSH + i),
						reg[A + i]
					)
			case 0x23: # close
				raise LuaError("Not implemented: close") # TODO
			case 0x24: # closure
				raise LuaError("Not implemented: closure") # TODO
			case 0x25: # vararg
				raise LuaError("Not implemented: vararg") # TODO
		
		pc += 1

