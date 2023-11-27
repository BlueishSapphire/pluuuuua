from luatypes import *
from luaenv import LuaEnv

import struct


class LuaFile:
	def __init__(self, filename: str, contents: str, env: LuaEnv = LuaEnv.get_default()):
		self.filename = filename
		self.contents = contents
		self.func_proto_num = 0
		self.position = 0
		self.env = env
		self.read_header()
		self.main_func = self.get_func()

	def execute(self, args: list[LuaObject] = []):
		try:
			return self.main_func.call(self.env, args)
		except LuaError as err:
			print("LuaError:", err)

	def read(self, num_bytes: int = 1) -> bytes:
		start = self.position
		end = start + num_bytes
		res = self.contents[start:end]
		self.position += num_bytes
		return res

	def get_byte(self):
		return int.from_bytes(self.read(1))

	def get_bytes(self, num_bytes: int):
		return [int.from_bytes(self.read(1)) for _ in range(num_bytes)]

	def get_int(self) -> int:
		return int.from_bytes(self.read(self.int_size), self.endianness)

	def get_size_t(self) -> int:
		return int.from_bytes(self.read(self.size_size), self.endianness)

	def get_str(self) -> str:
		size = self.get_size_t()
		return self.read(size).decode("utf-8")[:-1]

	def get_list(self, get_element: callable) -> list:
		size = self.get_int()
		return [get_element() for _ in range(size)]

	def get_instruct(self):
		return LuaInstruct(self.read(self.instruct_size))

	def get_bool(self) -> bool:
		return bool(self.get_byte())

	def get_number(self) -> int | float:
		return struct.unpack('d', self.read(self.number_size))[0]

	def get_const(self) -> None | bool | int | float | str:
		kind = self.get_byte()
		match kind:
			case 0: val = LuaNil()
			case 1: val = LuaBoolean(self.get_bool())
			case 3: val = LuaNumber(self.get_number())
			case 4: val = LuaString(self.get_str())
		return val

	def get_local(self) -> tuple[str, int, int]:
		return (self.get_str(), self.get_int(), self.get_int())

	def get_func(self):
		my_proto_num = self.func_proto_num
		self.func_proto_num += 1
		func = LuaFunction(
			proto_num=my_proto_num,
			source_name=self.get_str(),
			first_line_num=self.get_int(),
			last_line_num=self.get_int(),
			num_upvals=self.get_byte(),
			num_params=self.get_byte(),
			is_vararg=self.get_byte(),
			max_stack_size=self.get_byte(),
			instructs=self.get_list(self.get_instruct),
			consts=self.get_list(self.get_const),
			func_protos=self.get_list(self.get_func),
			line_positions=self.get_list(self.get_int),
			local_vars=self.get_list(self.get_local),
			upval_names=self.get_list(self.get_str),
		)
		return func

	def read_header(self) -> None:
		magic_bytes = self.get_bytes(4)
		self.lua_version = self.get_byte()
		self.format_version = self.get_byte()
		self.endianness = "little" if self.get_byte() == 1 else "big"
		self.int_size = self.get_byte()
		self.size_size = self.get_byte()
		self.instruct_size = self.get_byte()
		self.number_size = self.get_byte()
		self.is_integral = bool(self.get_byte())

		assert magic_bytes == list(b'\x1bLua'), "not a compiled lua file"
		assert self.lua_version == 0x51, "compiled with the wrong lua version (expected lua 5.1)"
		assert self.format_version == 0, "not the official format version"
		assert self.endianness == "little", "expected endianness to be little but it was big"
		assert self.int_size == 4, f"expected int size of 4, found {self.int_size}"
		assert self.size_size == 8, f"expected size_t size of 8, found {self.size_size}"
		assert self.instruct_size == 4, f"expected instruct size of 4, found {self.instruct_size}"
		assert self.number_size == 8, f"expected number size of 8, found {self.number_size}"
		assert not self.is_integral, "expected integral flag to be unset, but it was set"
