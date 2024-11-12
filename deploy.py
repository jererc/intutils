#!/bin/env python3
from glob import glob
import hashlib
import os
from pprint import pprint
import shutil
import subprocess


LIB_PATHS = [
    '~/data/code/svcutils',
    '~/data/code/webutils',
]
APP_PATHS = [
    '~/data/code/bfshuffle',
    '~/data/code/itemz/itemz',
    '~/data/code/savegame/savegame',
]
DEPLOY_PATH = '~/MEGA/data/code'


def get_file_hash(file, encoding='utf-8'):
    with open(file, 'r') as fd:
        return hashlib.md5(fd.read().encode(encoding)).hexdigest()


def is_valid_py_file(file):
    filename = os.path.basename(file)
    if filename == 'user_settings.py':
        return False
    if filename.startswith('test_'):
        return False
    return True


def list_py_files(path):
    files = glob(os.path.join(path, '*.py'))
    return {f for f in files if is_valid_py_file(f)}


def print_row(src_file, dst_file, status):
    print(f'{status:20}  {src_file:80} {dst_file}')


def copy_if_necessary(src_file, dst_file):
    if get_file_hash(src_file) == get_file_hash(dst_file):
        print_row(src_file, dst_file, 'OK')
    else:
        shutil.copyfile(src_file, dst_file)
        print_row(src_file, dst_file, 'updated')


def copy_libs():
    print('-' * 80)
    print_row('src', 'dst', 'lib status')
    for dst_path in APP_PATHS:
        for src_path in LIB_PATHS:
            src_path = os.path.expanduser(src_path)
            for src_file in sorted(list_py_files(src_path)):
                rel_path = os.path.relpath(src_file, src_path)
                dst_file = os.path.join(os.path.expanduser(dst_path), rel_path)
                if not os.path.exists(dst_file):
                    continue
                copy_if_necessary(src_file, dst_file)


def deploy():
    print('-' * 80)
    print_row('src', 'dst', 'deploy status')
    for src_path in APP_PATHS:
        src_path = os.path.expanduser(src_path)
        dst_path = os.path.join(os.path.expanduser(DEPLOY_PATH),
            os.path.basename(src_path))
        for src_file in sorted(list_py_files(src_path)):
            rel_path = os.path.relpath(src_file, src_path)
            dst_file = os.path.join(dst_path, rel_path)
            copy_if_necessary(src_file, dst_file)
        for dst_file in sorted(list_py_files(dst_path)):
            rel_path = os.path.relpath(dst_file, dst_path)
            src_file = os.path.join(src_path, rel_path)
            if not os.path.exists(src_file):
                print_row('', dst_file, 'missing at source')


def check_repos():
    for path in APP_PATHS:
        print('-' * 80)
        print(path)
        subprocess.check_call(['git', 'status'],
            cwd=os.path.expanduser(path))


def main():
    copy_libs()
    deploy()
    check_repos()


if __name__ == '__main__':
    main()
