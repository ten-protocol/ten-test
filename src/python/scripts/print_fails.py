# utility script to print out failing test ids
import os

fails = "ten_rob_002 gen_cor_112 gen_cor_132 ten_cor_002 ten_cor_004 ten_cor_005 ten_cor_018 ten_cor_019 ten_cor_090 ten_cor_091 ten_cor_092 ten_cor_093 gen_cor_120 gen_cor_121 gen_cor_122 gen_cor_123 gen_cor_124 gen_cor_125 gen_cor_126 ten_cor_050 ten_cor_051 ten_cor_033 ten_cor_152"
tests = fails.split()
tests.sort()

print(os.getcwd())
os.chdir('../../..')
for t in tests:
    os.system('pysys.py print %s' %t)