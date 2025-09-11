import argparse
import os
import re
import unicodedata

RE_REMOVE = re.compile(r'[\n\r]+')
RE_SPECIAL = re.compile(r'[\t\*\:\;\?\|\"\'\<\>]+')
RE_SPACE = re.compile(r'[\s_]+')


def walk_paths(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for item in sorted(files + dirs):
            yield os.path.join(root, item)


def iter_paths(paths):
    for path in paths:
        if not os.path.exists(path):
            print(f'path does not exist: {path}')
            continue
        for path_ in walk_paths(path):
            yield path_


def remove_accents(text):
    # Normalize the text to "NFD" form (decomposed)
    normalized = unicodedata.normalize('NFD', text)
    # Filter out all combining characters (accents, etc.)
    without_accents = ''.join(
        char for char in normalized
        if unicodedata.category(char) != 'Mn'
    )
    return without_accents


def remove_accents_ascii(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')


def clean(val):
    val = RE_REMOVE.sub('', val)
    val = RE_SPECIAL.sub('_', val)
    val = remove_accents(val)
    return RE_SPACE.sub('_', val).strip('_')


def get_new_path(path, dirname_callable=None, filename_callable=None):
    dirname, basename = os.path.split(path)

    def clean_filename(filename, is_dir=False):
        res = clean(filename)
        if is_dir and dirname_callable:
            res = dirname_callable(res)
        elif not is_dir and filename_callable:
            res = filename_callable(res)
        return res

    if os.path.isdir(path):
        return os.path.join(dirname, clean_filename(basename, is_dir=True))
    else:
        filename, ext = os.path.splitext(basename)
        return os.path.join(dirname,
                            f'{clean_filename(filename, is_dir=False)}{ext.lower()}')


def clean_paths(paths, dirname_callable=None, filename_callable=None, dry_run=False):
    for path in iter_paths(paths):
        new_path = get_new_path(path, dirname_callable=dirname_callable,
                                filename_callable=filename_callable)
        if not new_path or new_path == path:
            continue
        print(f'old: {path}\nnew: {new_path}')
        if not dry_run:
            os.rename(path.encode('utf-8'), new_path)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--lower', action='store_true')
    parser.add_argument('--lower_dir', action='store_true')
    parser.add_argument('--capitalize', action='store_true')
    parser.add_argument('--capitalize_dir', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


def _lower(x):
    return x.lower()


def _capitalize(x):
    return x.title()


def main():
    args = parse_args()
    if args.lower:
        filename_callable = _lower
    elif args.capitalize:
        filename_callable = _capitalize
    else:
        filename_callable = None
    if args.lower_dir:
        dirname_callable = _lower
    elif args.capitalize_dir:
        dirname_callable = _capitalize
    else:
        dirname_callable = None
    clean_paths(
        paths=args.paths,
        dirname_callable=dirname_callable,
        filename_callable=filename_callable,
        dry_run=args.dry_run,
    )


if __name__ == '__main__':
    main()
