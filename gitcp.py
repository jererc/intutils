#!/bin/env python3
from datetime import datetime
import os
import re
import subprocess


version = datetime.now().strftime('%Y.%m.%d.%H%M%S')

setup_file = os.path.join(os.getcwd(), 'setup.py')
if os.path.exists(setup_file):
    pattern = r'(version=[\'"])([^\'"]+)([\'"])'
    with open(setup_file, 'r', encoding='utf-8') as fd:
        content = fd.read()
    res = re.search(pattern, content)
    content = re.sub(pattern, f'{res.group(1)}{version}{res.group(3)}', content)
    with open(setup_file, 'w', encoding='utf-8') as fd:
        fd.write(content)

subprocess.check_call(['git', '--no-pager', 'diff'])
user_input = input('Do you want to commit? (yes/no): ').strip().lower()
if user_input in ['yes', 'y', '']:
    subprocess.check_call(['git', 'commit', '-am', 'do epic things'])
    subprocess.check_call(['git', 'push'])
    print(f'{version=}')
