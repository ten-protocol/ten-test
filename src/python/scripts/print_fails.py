# utility script to print out failing test ids
import os

fails = ""
tests = fails.split()
tests.sort()

print(os.getcwd())
os.chdir('../../..')
for t in tests:
    os.system('pysys.py print %s' %t)