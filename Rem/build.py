from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
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
