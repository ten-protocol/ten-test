# utility script to print out failing test ids
import os

fails = "ten_cor_027 ten_cor_046 gen_cor_091"
tests = fails.split()
tests.sort()

print(os.getcwd())
os.chdir('../../..')
for t in tests:
    os.system('pysys.py print %s' %t)