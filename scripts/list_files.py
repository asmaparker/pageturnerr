import os
import sys
import glob

files = glob.glob(pathname=pathname="D:\\Downloads\\asmaaa\\*.json")

for file in files:
    data = file.json()
    