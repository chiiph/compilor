from distutils.core import setup
import py2exe
import sys

def py_exe(file_in=None):
    if len(sys.argv) == 1:
        sys.argv.append('py2exe')

setup(options = {'py2exe': {'compressed': 1, 'optimize': 2, 'ascii': 1, 'bundle_files': 3 }}, zipfile = None,
           ## Can use console or window
           ## Filpath to '....py' or same folder as you run this py file from
           console = [{'script': 'lexor_main.py'}])