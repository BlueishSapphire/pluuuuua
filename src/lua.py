from luafile import *
from luatypes import *
from luaenv import *

import subprocess

input_filename = "example.lua"

res = subprocess.call(["luac5.1", input_filename])

source_file = LuaFile("luac.out")
source_file.execute()
