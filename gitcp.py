#!/bin/env python3
from datetime import datetime
import os
import re
import subprocess

pattern = r'(version=[\'"])([^\'"]+)([\'"])'

version = datetime.now().strftime('%Y.%m.%d.%H%M%S')
print(f'{version=}')

with open('setup.py', 'r', encoding='utf-8') as fd:
    content = fd.read()

res = re.search(pattern, content)
content = re.sub(pattern, f'{res.group(1)}{version}{res.group(3)}', content)
print(content)

with open('setup.py', 'w', encoding='utf-8') as fd:
    fd.write(content)

subprocess.check_call(['git', 'diff'])
user_input = input('Do you want to commit? (yes/no): ').strip().lower()
if user_input in ['yes', 'y', '']:
    subprocess.check_call(['git', 'commit', '-am', 'do epic things'])
    subprocess.check_call(['git', 'push', 'origin', 'main'])

