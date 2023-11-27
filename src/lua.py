from luafile import LuaFile
import lvm

import subprocess

# input_filename = "examples/binsearch/binsearch.lua"
input_filename = "example.lua"

res = subprocess.call(["luac5.1", input_filename])

with open("luac.out", "rb") as f:
	source_file = LuaFile("luac.out", f.read())
	res = source_file.execute()

