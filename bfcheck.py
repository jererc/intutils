from glob import glob
import hashlib
import json
import os
from pprint import pprint
import time


def walk_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)


def get_file_hash(file, chunk_size=8192):
    if not os.path.exists(file):
        return None
    md5_hash = hashlib.md5()
    with open(file, 'rb') as fd:
        while chunk := fd.read(chunk_size):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def main():
    src_path = r'D:\SteamLibrary\steamapps\common\Battlefield 2042'
    dst_prefix = 'bf-'

    hashes = {}
    files = list(walk_files(src_path))
    for i, file in enumerate(files):
        print(f'processing {file} ({i + 1} / {len(files)})')
        hashes[file] = get_file_hash(file)

    base_dst = os.path.expanduser('~')
    dst_path = os.path.join(base_dst, f'{dst_prefix}{int(time.time())}.json')
    with open(dst_path, 'w') as fd:
        fd.write(json.dumps(hashes))

    dst_files = sorted(glob(os.path.join(base_dst, f'{dst_prefix}*')))
    if len(dst_files) > 1:
        with open(dst_files[-2]) as fd:
            old_hashes = json.load(fd)
        for f, h in old_hashes.items():
            new_h = hashes.get(f)
            if not new_h:
                print(f'missing file: {f}')
            elif new_h != h:
                print(f'invalid file: {f} (old: {h} / new: {new_h})')


# invalid file: D:\SteamLibrary\steamapps\common\Battlefield 2042\EAAntiCheat.GameServiceLauncher.dll (old: 1763db71b72d861132d8d368ab91c834 / new: 088ca64f7e4ddae324bc07c1c665f304)
# invalid file: D:\SteamLibrary\steamapps\common\Battlefield 2042\EAAntiCheat.GameServiceLauncher.exe (old: ff5e84f6a632a7d0a37830ae7513b8a0 / new: af5da4d52bdae0a55f24e15fd83db221)
# invalid file: D:\SteamLibrary\steamapps\common\Battlefield 2042\preloader_l.dll (old: 0ce436fd778db376c47f6f918cbf3dae / new: 4f5381a454e80485bb43d29c5a301634)

# invalid file: D:\SteamLibrary\steamapps\common\Battlefield 2042\EAAntiCheat.GameServiceLauncher.dll (old: 1763db71b72d861132d8d368ab91c834 / new: 088ca64f7e4ddae324bc07c1c665f304)
# missing file: D:\SteamLibrary\steamapps\common\Battlefield 2042\EAAntiCheat.GameServiceLauncher.dll_b
# invalid file: D:\SteamLibrary\steamapps\common\Battlefield 2042\EAAntiCheat.GameServiceLauncher.exe (old: ff5e84f6a632a7d0a37830ae7513b8a0 / new: af5da4d52bdae0a55f24e15fd83db221)
# missing file: D:\SteamLibrary\steamapps\common\Battlefield 2042\EAAntiCheat.GameServiceLauncher.exe_b
# invalid file: D:\SteamLibrary\steamapps\common\Battlefield 2042\preloader_l.dll (old: 0ce436fd778db376c47f6f918cbf3dae / new: 4f5381a454e80485bb43d29c5a301634)
# missing file: D:\SteamLibrary\steamapps\common\Battlefield 2042\preloader_l.dll_b


if __name__ == "__main__":
    main()
