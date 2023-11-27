from luatypes import *
from luaenv import LuaEnv


debug = True


class LuaStack:
	def __init__(self, max_stack_size: int):
		self.max_stack_size = max_stack_size
		self.registers = [None] * max_stack_size
		self.pool = {}

	def __getitem__(self, idx: int | slice):
		return self.registers[idx]

	def __setitem__(self, idx: int, val: LuaObject):
		assert isinstance(val, LuaObject), "tried to set a non-lua value to a register"
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

	def pop(self, idx: int):
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
		self.parent.pop(self.idx)


def not_none(l: list) -> list:
	return list(filter(lambda a: a is not None, l))


def call_lua_function(lua_func, env: LuaEnv, args: list[LuaObject]):
	pc = 0
	stack = LuaStack(lua_func.max_stack_size)
	for i in range(len(args)):
		stack[i] = args[i]
	const = lua_func.consts
	upval = lua_func.upvals

	if debug:
		upval_names = lua_func.upval_names
		local_names = lua_func.local_vars

	def stack_or_const(val: int):
		return const[val ^ 256] if val & 256 else stack[val]

	if debug:
		print(lua_func.get_debug_str())

	while pc < len(lua_func.instructs):
		inst = lua_func.instructs[pc]
		A, B, C, Bx, sBx = inst.A, inst.B, inst.C, inst.Bx, inst.sBx

		if debug:
			print("\x1b[3J\x1b[H", end="")
			print(lua_func.get_debug_str())
			registers = [v or LuaNil() for v in stack.registers]
			for [name, _, _], val in zip(local_names, registers):
				print(f"-> {name} = {repr(val)}")
			extra_stack = registers[len(local_names):]
			print(f"-> [{', '.join(repr(v) for v in extra_stack)}]")
			input(f"{lua_func.proto_num}:[{pc + 1}] {inst.name}")

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
				stack[A].set(stack_or_const(B), stack_or_const(C))
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
				stack[A] = reduce(lambda l, r: l.op_concat(r), stack[B:C + 1])
				# stack[A] = LuaString("".join(map(lambda s: s.tostring(), stack[B:C + 1])))
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
				if (stack[B] is not None and stack[B].bool()) != bool(C):
					pc += 1
			case 0x1B: # testset
				if (stack[B] is not None and stack[B].bool()) != bool(C):
					pc += 1
				else:
					stack[A] = stack[B] or LuaNil()
			case 0x1C: # call
				if B == 1:
					args = []
				elif B == 0:
					args = stack[A + 1:]
				else:
					args = stack[A + 1:A + B]

				args = not_none(args)

				if debug: print(f"call: args {args}")
				res = stack[A].call(env, args)

				for i in range(A, len(stack)):
					stack.pop(A)

				num_res = (C - 1) if C >= 1 else len(res)
				if debug: print(f"call: returned with {num_res} results {res}")

				for i in range(num_res):
					stack[A + i] = res[i] if i < len(res) else LuaNil()
			case 0x1D: # tail_call
				if B == 1:
					args = []
				elif B == 0:
					args = stack[A + 1:]
				else:
					args = stack[A + 1:A + B]

				args = not_none(args)

				if debug: print(f"tailcall: args {args}")
				res = stack[A].call(env, args)

				for i in range(A, len(stack)):
					stack.pop(A)

				if debug: print(f"tailcall: returning with {len(res)} results {res}")
				return res
			case 0x1E: # return
				if B == 1:
					res = (LuaNil(),)
				elif B == 0:
					res = tuple(stack[A:])
				else:
					res = tuple(stack[A:A + B - 1])

				for i in range(A, len(stack)):
					stack.pop(A)

				if debug: print(f"return: returning with {len(res)} results {res}")
				return res
			case 0x1F: # forloop
				stack[A] = stack[A].op_add(stack[A + 2])
				if stack[A] <= stack[A + 1]:
					pc += sBx
					stack[A + 3] = stack[A]
			case 0x20: # forprep
				stack[A] = stack[A].op_sub(stack[A + 2])
				pc += sBx
			case 0x21: # tforloop
				res = stack[A].call(env, [stack[A + 1], stack[A + 2]])
				
				for i in range(0, C):
					stack[A + 3 + i] = res[i]

				if not isinstance(stack[A + 3], LuaNil):
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
					stack[A].set(
						((C - 1) * LFIELDS_PER_FLUSH + i),
						stack[A + i]
					)
			case 0x23: # close
				for i in range(A, len(stack)):
					stack.pop(i)
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
