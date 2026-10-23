"""Index local evidence files with sizes and SHA-256 hashes; never infer event metadata."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path


def index(root, output):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Input must be a directory.')
    output = output.resolve()
    entries, skipped = [], []
    def walk_error(exc):
        p = Path(exc.filename) if exc.filename else root
        label = p.relative_to(root).as_posix() if p.is_relative_to(root) else p.name
        skipped.append({'path': label, 'reason': type(exc).__name__})
    for folder, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        for name in dirs[:]:
            p = Path(folder)/name
            if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
                dirs.remove(name)
                skipped.append({'path': p.relative_to(root).as_posix(), 'reason': 'directory_link'})
        for name in sorted(files):
            p = Path(folder)/name
            rel = p.relative_to(root).as_posix()
            try:
                if p.is_symlink() or not p.resolve().is_relative_to(root):
                    skipped.append({'path': rel, 'reason': 'link_or_outside_root'})
                    continue
                if p.resolve() == output:
                    continue
                before = p.stat()
                digest = hashlib.sha256()
                with p.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024 * 1024), b''):
                        digest.update(chunk)
                after = p.stat()
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    skipped.append({'path': rel, 'reason': 'changed_during_read'})
                    continue
                entries.append({'path': rel, 'bytes': before.st_size, 'sha256': digest.hexdigest(),
                                'filesystem_modified_utc': datetime.fromtimestamp(before.st_mtime, timezone.utc).isoformat()})
            except OSError as exc:
                skipped.append({'path': rel, 'reason': type(exc).__name__})
    entries.sort(key=lambda x: x['path'])
    duplicates = {}
    for row in entries:
        duplicates.setdefault(row['sha256'], []).append(row['path'])
    return {'files': entries, 'byte_identical_groups': [v for v in duplicates.values() if len(v)>1],
            'skipped': skipped, 'note': 'File modification time is not capture time. A hash proves byte identity, not event identity.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_directory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    try:
        result = index(a.input_directory, a.output)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        with a.output.open('x', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
