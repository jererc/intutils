from datetime import datetime
import os
import re
import subprocess
import time


BIN_PATH = {'nt': r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe',
            'posix': '/usr/bin/VBoxManage',
            }[os.name]
OUTPUT_PATH = os.path.join(os.path.expanduser('~'), 'exported_vms')


class VMManage:
    def __init__(self, output_path=OUTPUT_PATH):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def _parse_list_output(self, stdout):
        return {r.rsplit(None, 1)[0].strip('"')
                for r in stdout.decode('utf-8').splitlines()}

    def list_all(self):
        stdout = subprocess.check_output([BIN_PATH, 'list', 'vms'])
        return self._parse_list_output(stdout)

    def list_running(self):
        stdout = subprocess.check_output([BIN_PATH, 'list', 'runningvms'])
        return self._parse_list_output(stdout)

    def _wait_for_stopped(self, vm, timeout=20):
        end_ts = time.time() + timeout
        while time.time() < end_ts:
            if vm not in self.list_running():
                return
            time.sleep(1)
        raise Exception(f'timed out waiting for {vm} to stop')

    def stop(self, vm):
        print(f'stopping {vm}')
        try:
            subprocess.check_call([BIN_PATH, 'controlvm', vm, 'acpipowerbutton'])
            self._wait_for_stopped(vm)
        except subprocess.CalledProcessError:
            print(f'failed to stop {vm}')

    def _get_export_file(self, vm):
        name = re.sub(r'\W+', '_', vm)
        today = datetime.now().strftime('%Y%m%d')
        return os.path.join(self.output_path, f'{name}-{today}.ova')

    def export(self, vm, file):
        start_ts = time.time()
        print(f'exporting {vm}')
        try:
            subprocess.check_call([BIN_PATH, 'export', vm, '--output', file])
            print(f'exported {vm} in {time.time() - start_ts:.02f} seconds')
        except subprocess.CalledProcessError:
            print(f'failed to export {vm}')

    def export_all(self):
        running = self.list_running()
        for vm in self.list_all():
            if vm.startswith('test'):
                print(f'skipping {vm}')
                continue
            file = self._get_export_file(vm)
            if os.path.exists(file):
                print(f'{file} already exists')
                continue
            if vm in running:
                self.stop(vm)
            self.export(vm, file)


def main():
    VMManage().export_all()


if __name__ == '__main__':
    main()
