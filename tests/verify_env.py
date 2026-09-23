import sys
import subprocess
import os

print("python_version:", sys.version.replace('\n',' '))
print("executable:", sys.executable)
try:
    pip_out = subprocess.check_output([sys.executable, "-m", "pip", "--version"], stderr=subprocess.STDOUT)
    print("pip_version:", pip_out.decode().strip())
except Exception as e:
    print("pip_version: ERROR -", e)
print("cwd:", os.getcwd())
print("basic_check: PASS")
