#!/usr/bin/env python3
import argparse
from contextlib import contextmanager
import os
import subprocess
import sys
import time

TMP_FILE = '/tmp/tmpfile'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shutdown', action='store_true', help='shutdown after cleaning')
    return parser.parse_args()


def run_command(cmd, description, **kwargs):
    print('*' * 80)
    print(description)
    try:
        subprocess.run(cmd, text=True, stdout=sys.stdout, stderr=sys.stderr, **kwargs)
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
        print(f'Output: {e.stdout}')
        return False
    return True


def optimize_free_space(tmp_file=TMP_FILE):
    run_command(f'dd if=/dev/zero of={tmp_file} bs=8M', 'optimizing free space (creating tmp file)', shell=True)
    run_command(f'rm {tmp_file}', 'optimizing free space (cleaning tmp file)', shell=True)


def get_drive_usage():
    run_command('sudo du -ah / | sort -hr | head -n 50', 'getting drive usage', shell=True)


class MegasyncManager:
    cmd = 'megasync'

    def is_running(self):
        result = subprocess.run(['pgrep', '-x', self.cmd], capture_output=True)
        return result.returncode == 0

    def stop(self):
        subprocess.run(['pkill', '-SIGTERM', self.cmd], check=False)
        while self.is_running():
            print(f'waiting for {self.cmd} to stop...')
            time.sleep(1)
        print(f'{self.cmd} stopped successfully')

    def start(self):
        try:
            subprocess.Popen([self.cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            print(f'{self.cmd} started successfully')
        except Exception as e:
            print(f'Failed to start {self.cmd}: {e}')
            return False
        return True

    @contextmanager
    def not_running(self):
        running = self.is_running()
        if running:
            print(f'stopping {self.cmd}...')
            self.stop()
        yield
        if running:
            print(f'restarting {self.cmd}...')
            self.start()


def main():
    if os.path.exists(TMP_FILE):
        os.remove(TMP_FILE)
    args = get_args()
    run_command('rm -rf ~/.local/share/Trash/files/*', 'emptying trash files', shell=True)
    run_command('rm -rf ~/.local/share/Trash/info/*', 'emptying trash info', shell=True)
    run_command('sudo journalctl --vacuum-time=2d', 'cleaning logs', shell=True)
    run_command('sudo apt -y clean', 'cleaning apt cache', shell=True)
    run_command('sudo apt -y autoclean', 'cleaning apt cache', shell=True)
    run_command('sudo apt -y autoremove', 'cleaning apt cache', shell=True)
    run_command('sudo rm -rf /var/lib/snapd/cache/*', 'cleaning snap cache', shell=True)
    run_command('sudo docker system prune -a --volumes -f', 'cleaning docker system', shell=True)
    with MegasyncManager().not_running():
        optimize_free_space()
    get_drive_usage()
    if args.shutdown:
        run_command('sudo shutdown -h now', 'shutting down', shell=True)


if __name__ == "__main__":
    main()
