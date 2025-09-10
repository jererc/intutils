import os
import urllib.request

url = 'https://raw.githubusercontent.com/jererc/svcutils/refs/heads/main/svcutils/bootstrap.py'
exec(urllib.request.urlopen(url).read().decode('utf-8'))
Bootstrapper(
    name='intutils',
    install_requires=[
        # 'git+https://github.com/jererc/intutils.git',
        'intutils @ https://github.com/jererc/intutils/archive/refs/heads/main.zip',
    ],
    force_reinstall=True,
).setup_venv()
