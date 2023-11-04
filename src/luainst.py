from enum import Enum, auto


class InstructKind(Enum):
	iA = auto()
	iAB = auto()
	iABx = auto()
	iAsBx = auto()
	isBx = auto()
	iAC = auto()
	iABC = auto()


INSTRUCT_DESCRIPTIONS = {
	0x00: ('move',      InstructKind.iAB),
	0x01: ('loadk',     InstructKind.iABx),
	0x02: ('loadbool',  InstructKind.iABC),
	0x03: ('loadnil',   InstructKind.iAB),
	0x04: ('getupval',  InstructKind.iAB),
	0x05: ('getglobal', InstructKind.iABx),
	0x06: ('gettable',  InstructKind.iABC),
	0x07: ('setglobal', InstructKind.iABx),
	0x08: ('setupval',  InstructKind.iAB),
	0x09: ('settable',  InstructKind.iABC),
	0x0A: ('newtable',  InstructKind.iABC),
	0x0B: ('self',      InstructKind.iABC),
	0x0C: ('add',       InstructKind.iABC),
	0x0D: ('sub',       InstructKind.iABC),
	0x0E: ('mul',       InstructKind.iABC),
	0x0F: ('div',       InstructKind.iABC),
	0x10: ('mod',       InstructKind.iABC),
	0x11: ('pow',       InstructKind.iABC),
	0x12: ('unm',       InstructKind.iAB),
	0x13: ('not',       InstructKind.iAB),
	0x14: ('len',       InstructKind.iAB),
	0x15: ('concat',    InstructKind.iABC),
	0x16: ('jmp',       InstructKind.isBx),
	0x17: ('eq',        InstructKind.iABC),
	0x18: ('lt',        InstructKind.iABC),
	0x19: ('le',        InstructKind.iABC),
	0x1A: ('test',      InstructKind.iAC),
	0x1B: ('testset',   InstructKind.iABC),
	0x1C: ('call',      InstructKind.iABC),
	0x1D: ('tailcall',  InstructKind.iABC),
	0x1E: ('return',    InstructKind.iAB),
	0x1F: ('forloop',   InstructKind.iAsBx),
	0x20: ('forprep',   InstructKind.iAsBx),
	0x21: ('tforloop',  InstructKind.iAC),
	0x22: ('setlist',   InstructKind.iABC),
	0x23: ('close',     InstructKind.iA),
	0x24: ('closure',   InstructKind.iABx),
	0x25: ('vararg',    InstructKind.iAB),
}


# BBBBBBBB BCCCCCCC CCAAAAAA AAOOOOOO
OPCODE_OFFSET = 0
OPCODE_SIZE = 6
A_OFFSET = OPCODE_OFFSET + OPCODE_SIZE
A_SIZE = 8
C_OFFSET = A_OFFSET + A_SIZE
C_SIZE = 9
B_OFFSET = C_OFFSET + C_SIZE
B_SIZE = 9


OPCODE_MASK = ((1 << OPCODE_SIZE) - 1) << OPCODE_OFFSET
A_MASK = ((1 << A_SIZE) - 1) << A_OFFSET
B_MASK = ((1 << B_SIZE) - 1) << B_OFFSET
C_MASK = ((1 << C_SIZE) - 1) << C_OFFSET


class LuaInstruct:
	def __init__(self, raw: bytes):
		self.raw_int = int.from_bytes(raw, "little")
		self.raw = list(reversed(raw)) # little endian

		self.opcode = (self.raw_int & OPCODE_MASK) >> OPCODE_OFFSET
		self.A = (self.raw_int & A_MASK) >> A_OFFSET
		self.B = (self.raw_int & B_MASK) >> B_OFFSET
		self.C = (self.raw_int & C_MASK) >> C_OFFSET

		# Bx is B and C combined into a single 18 bit int
		self.Bx = (self.B << 9) | self.C
		# sBx is signed Bx
		self.sBx = self.Bx - 131071

		self.name, self.kind = INSTRUCT_DESCRIPTIONS[self.opcode]

	def __str__(self):
		res = self.name + "("
		match self.kind:
			case InstructKind.iA:
				res += "A"
			case InstructKind.iAB:
				res += "A, B"
			case InstructKind.iABx:
				res += "A, Bx"
			case InstructKind.iAsBx:
				res += "A, sBx"
			case InstructKind.isBx:
				res += "sBx"
			case InstructKind.iAC:
				res += "A, C"
			case InstructKind.iABC:
				res += "A, B, C"
		res += ")"
		return res

	def __repr__(self):
		res = f"LuaInstruct(0x{self.raw_int:08X}, {self.name}, "
		match self.kind:
			case InstructKind.iA:
				res += "A"
			case InstructKind.iAB:
				res += "A, B"
			case InstructKind.iABx:
				res += "A, Bx"
			case InstructKind.iAsBx:
				res += "A, sBx"
			case InstructKind.isBx:
				res += "sBx"
			case InstructKind.iAC:
				res += "A, C"
			case InstructKind.iABC:
				res += "A, B, C"
		res += ")"
		return res
