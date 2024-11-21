# utility script to print out failing test ids
import os

fails = "ten_cor_023 ten_cor_034 ten_cor_024 ten_cor_025 ten_cor_022 ten_cor_020 ten_cor_021 ten_cor_027 ten_cor_026"
tests = fails.split()
tests.sort()

print(os.getcwd())
os.chdir('../../..')
for t in tests:
    os.system('pysys.py print %s' %t)