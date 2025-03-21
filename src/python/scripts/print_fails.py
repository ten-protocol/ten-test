# utility script to print out failing test ids
import os

fails = "ten_cor_026 ten_cor_021 ten_cor_024 ten_cor_025 ten_cor_028"
tests = fails.split()
tests.sort()

print(os.getcwd())
os.chdir('../../..')
for t in tests:
    os.system('pysys.py print %s' %t)