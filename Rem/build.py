from cx_Freeze import setup, Executable

import sys
assert sys.version_info[0]==2
if len(sys.argv)==1:
    sys.argv.append('build')

buildOptions = dict(packages = ['Queue'], excludes = [])

import sys
base = 'Win32Gui' if sys.platform=='win32' else None

executables = [
    Executable('rem.py', base=base)
]

setup(name='rem',
      version = '1.0',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)

import os
import shutil
shutil.copyfile('addr.txt','build/exe.win32-2.7/addr.txt')
os.remove('build/exe.win32-2.7/_hashlib.pyd')
os.remove('build/exe.win32-2.7/_ssl.pyd')