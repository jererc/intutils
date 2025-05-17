#!/usr/bin/env python3
import ctypes
import os
from pprint import pprint
import subprocess
import string
import sys


SRC_LABEL = 'extdrive'
DST_LABELS = {'extdrive2', 'extdrive3'}
DATA_DIR = 'data'

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


def list_windows_volumes():
    """Return a list of (root_path, label) tuples such as ('C:\\', 'System')."""
    mask = kernel32.GetLogicalDrives()                # bitmask of existing letters
    result = []

    for i, ch in enumerate(string.ascii_uppercase):     # A … Z
        if not (mask & (1 << i)):
            continue                                    # letter not present
        root = f"{ch}:\\"

        # Buffers for the label and (unused here) filesystem name
        label_buf = ctypes.create_unicode_buffer(261)
        fs_buf = ctypes.create_unicode_buffer(261)

        ok = kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(root),          # lpRootPathName
            label_buf,                       # lpVolumeNameBuffer
            len(label_buf),                  # nVolumeNameSize (chars)
            None, None, None,                # serial, comp.len, flags – unused
            fs_buf,                          # lpFileSystemNameBuffer
            len(fs_buf)                      # nFileSystemNameSize (chars)
        )
        result.append((root, label_buf.value if ok else ""))

    return result


def get_src_and_dsts():
    label_roots = {l: r for r, l in list_windows_volumes()}
    pprint(label_roots)
    try:
        src_dir = os.path.join(label_roots[SRC_LABEL], DATA_DIR)
    except KeyError:
        print(f'missing src label {SRC_LABEL}')
        sys.exit(1)
    dst_dirs = []
    for dst_label in DST_LABELS:
        try:
            dst_dirs.append(os.path.join(label_roots[dst_label], DATA_DIR))
        except KeyError:
            continue
    if not dst_dirs:
        print(f'missing dst labels {DST_LABELS}')
        sys.exit(1)
    return src_dir, dst_dirs


def exec_cmd(cmd):
    # bufsize=1 → line-buffered;  text=True → str instead of bytes
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,   # robocopy writes progress to stderr too
        text=True,
        bufsize=1,
        universal_newlines=True     # <= Py3.6 compatibility
    ) as proc:
        for line in proc.stdout:          # iterates until robocopy exits
            print(line, end="")           # echo live progress

    if proc.returncode >= 8:
        raise RuntimeError(f"Robocopy failed (exit code {proc.returncode})")


def main():
    src_dir, dst_dirs = get_src_and_dsts()
    print(f'ready to sync {src_dir} to {dst_dirs}')
    input('press enter to continue...')
    for dst_dir in dst_dirs:
        cmd = ['robocopy', src_dir, dst_dir, '/MIR']
        print(f'running {cmd=}')
        exec_cmd(cmd)
    print(f'successfully synced {src_dir} to {dst_dirs}')


if __name__ == "__main__":
    main()
