from lib.common import *
import math
from ctypes import CDLL
libc = CDLL("libc.so.6")


def _mathfunc(name, f):
	def newf(*args):
		required_arg(name, args, 1, "number")
		return f(args[0].value)
	
	return newf


_min = min
def min(*args):
	required_arg("min", args, 1, "number")
	all_args("min", args, "number")
	return _min(map(lambda a: a.value, args))

_max = max
def max(*args):
	required_arg("max", args, 1, "number")
	all_args("min", args, "number")
	return _max(map(lambda a: a.value, args))

sqrt = _mathfunc("sqrt", math.sqrt)
log = _mathfunc("log", math.log)
log10 = _mathfunc("log10", math.log10)

deg = _mathfunc("deg", math.degrees)
rad = _mathfunc("rad", math.radians)

sin = _mathfunc("sin", math.sin)
asin = _mathfunc("asin", math.asin)
sinh = _mathfunc("sinh", math.sinh)

cos = _mathfunc("cos", math.cos)
acos = _mathfunc("acos", math.acos)
cosh = _mathfunc("cosh", math.cosh)

tan = _mathfunc("tan", math.tan)
atan = _mathfunc("atan", math.atan)
tanh = _mathfunc("tanh", math.tanh)
atan2 = _mathfunc("atan2", math.atan2)

exp = _mathfunc("exp", math.exp)
frexp = _mathfunc("exp", math.frexp)
ldexp = _mathfunc("exp", math.ldexp)

_abs = abs
abs = _mathfunc("exp", _abs)
floor = _mathfunc("exp", math.floor)
ceil = _mathfunc("exp", math.ceil)

# deprecated
def mod(*args):
	required_arg("mod", args, 1, "number")
	required_arg("mod", args, 2, "number")
	return args[0].value % args[1].value

def fmod(*args):
	required_arg("fmod", args, 1, "number")
	required_arg("fmod", args, 2, "number")
	return args[0].value % args[1].value

def modf(*args):
	required_arg("modf", args, 1, "number")
	required_arg("modf", args, 2, "number")
	return divmod(args[0].value, args[1].value)

_pow = pow
def pow(*args):
	required_arg("pow", args, 1, "number")
	required_arg("pow", args, 2, "number")
	return pow(args[0].value, args[1].value)


RAND_MAX = 2147483647

def _rand():
	return libc.rand() % RAND_MAX

def _srand(seed):
	libc.srand(math.floor(seed))

def randomseed(*args):
	optional_arg("randomseed", args, 1, "number")
	_srand(args[0].value)

def random(*args):
	optional_arg("random", args, 1, "number")
	optional_arg("random", args, 2, "number")
	
	r = (_rand() % RAND_MAX) / RAND_MAX
	
	if len(args) == 0:
		return r
	elif len(args) == 1:
		u = args[0].value
		if u <= 1:
			from luatypes import LuaError
			raise LuaError("interval is empty")
		return math.floor(r * u) + 1
	elif len(args) == 2:
		l = args[0].value
		u = args[1].value
		if l >= u:
			from luatypes import LuaError
			raise LuaError("interval is empty")
		return math.floor(r * (u - l + 1)) + l
	else:
		raise LuaError("wrong number of arguments")


pi = 3.1415926535898
huge = float("inf")


lua_mathlib = {
	"min": min,
	"max": max,
	"sqrt": sqrt,
	"log": log,
	"log10": log10,
	"deg": deg,
	"rad": rad,
	"sin": sin,
	"asin": asin,
	"sinh": sinh,
	"cos": cos,
	"acos": acos,
	"cosh": cosh,
	"tan": tan,
	"atan": atan,
	"tanh": tanh,
	"atan2": atan2,
	"exp": exp,
	"frexp": frexp,
	"ldexp": ldexp,
	"abs": abs,
	"floor": floor,
	"ceil": ceil,
	"mod": mod,
	"fmod": fmod,
	"modf": modf,
	"pow": pow,
	"random": random,
	"randomseed": randomseed,
	"pi": pi,
	"huge": huge,
}
