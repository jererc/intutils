import json
import logging
import os
from pathlib import PurePath
import re
import string
import time

NAME = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]
HOME_PATH = os.path.expanduser('~')
WORK_PATH = os.path.join(HOME_PATH, f'.{NAME}')
TRACKER_RUN_DELTA = 8 * 3600
TRACKER_MTIME_DELTA = 7 * 24 * 3600
TRACKER_PARENT_EXCLUSIONS = {r'C:\Windows'}
TRACKER_EXT_EXCLUSIONS = {'.lock', '.log', '.tmp'}
TRACKER_DIR_EXCLUSIONS = {
    'ASUS', 'Google', 'Intel', 'Microsoft', 'NVIDIA', 'NVIDIA Corporation',
    '$Recycle.Bin', 'OneDrive', 'OneDriveTemp', 'Packages'
}
TRACKER_REGEX_EXCLUSIONS = [
    re.compile(r'(cache|logs)([\W_]|$)', re.I),
]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


TRACKER_PARENT_EXCLUSIONS = {r'C:\Windows', r'D:\data\savegame'}


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def walk_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)


def to_json(data):
    return json.dumps(data, indent=4, sort_keys=True)


class DataTracker:
    file = os.path.join(WORK_PATH, 'tracker.json')

    def __init__(self):
        data = self._load()
        self.ts = data.get('ts', time.time() - TRACKER_MTIME_DELTA)
        self.tracked_paths = data.get('tracked_paths', {})
        self.modified_paths = data.get('modified_paths', {})

    def _load(self):
        try:
            with open(self.file) as fd:
                return json.load(fd)
        except Exception:
            return {}

    def _save(self):
        with open(self.file, 'w') as fd:
            fd.write(to_json({
                'ts': int(time.time()),
                'tracked_paths': self.tracked_paths,
                'modified_paths': self.modified_paths,
            }))

    def _iterate_root_paths(self):
        if os.name == 'nt':
            for drive in string.ascii_uppercase:
                path = f'{drive}:\\'
                if os.path.exists(path):
                    yield path
        else:
            yield os.path.expanduser('~')

    def _validate_path(self, pp):
        if str(pp) == self.file:
            return False
        if pp.suffix.lower() in TRACKER_EXT_EXCLUSIONS:
            return False
        if TRACKER_DIR_EXCLUSIONS & set(pp.parts):
            return False
        for parent_excl in TRACKER_PARENT_EXCLUSIONS:
            if pp.is_relative_to(parent_excl):
                return False
        parent = str(pp.parent)
        for regex in TRACKER_REGEX_EXCLUSIONS:
            if regex.search(parent):
                return False
        return True

    def _iterate_input_paths(self):
        for root_path in self._iterate_root_paths():
            for file in walk_files(root_path):
                pp = PurePath(file)
                if self._validate_path(pp):
                    yield pp

    def run(self, force=False):
        if not (force or time.time() > self.ts + TRACKER_RUN_DELTA):
            return
        start_ts = time.time()
        prev_tracked_paths = set(self.tracked_paths.keys())
        prev_modified_paths = set(self.modified_paths.keys())
        input_paths = set()
        for pp in self._iterate_input_paths():
            path = str(pp.parent)
            input_paths.add(path)
            try:
                mtime = os.stat(str(pp)).st_mtime
            except Exception:
                continue
            if mtime < self.ts:
                continue
            if mtime <= self.tracked_paths.get(path, 0):
                continue
            self.tracked_paths[path] = mtime
            if path in prev_tracked_paths:
                self.modified_paths[path] = pp.name

        self.tracked_paths = {k: v for k, v in self.tracked_paths.items()
                              if k in input_paths}
        logger.debug(f'processed {len(self.tracked_paths.keys())}'
                     f'/{len(input_paths)} paths '
                     f'in {time.time() - start_ts:.02f} seconds')
        new_modified_paths = {k: v for k, v in self.modified_paths.items()
                              if k not in prev_modified_paths}
        if new_modified_paths:
            files = [os.path.join(k, v) for k, v in new_modified_paths.items()]
            logger.info(f'modified files:\n{to_json(sorted(files))}')
        self._save()


def main():
    makedirs(WORK_PATH)
    DataTracker().run(force=True)


if __name__ == '__main__':
    main()
