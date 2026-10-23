"""Profile a local rectangular CSV without modifying or automatically cleaning it."""
import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
from collections import Counter


def profile(path, missing, key_columns, time_column):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        if not fields or len(fields) != len(set(fields)) or any(not x.strip() for x in fields):
            raise ValueError('CSV needs non-empty unique column names.')
        requested = key_columns + ([time_column] if time_column else [])
        if not set(requested) <= set(fields):
            raise ValueError('A key or time column is absent.')
        rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError('Non-rectangular CSV.')
    fingerprints = Counter(tuple(row[k] for k in fields) for row in rows)
    columns = {}
    for field in fields:
        numbers, invalid, missing_count, non_finite = [], 0, 0, 0
        for row in rows:
            value = row[field].strip()
            if value in missing:
                missing_count += 1
                continue
            try:
                number = float(value)
                if math.isfinite(number):
                    numbers.append(number)
                else:
                    non_finite += 1
            except ValueError:
                invalid += 1
        columns[field] = {'missing': missing_count, 'numeric_parseable': len(numbers),
                          'non_numeric': invalid, 'non_finite': non_finite,
                          'numeric_min': min(numbers) if numbers else None,
                          'numeric_max': max(numbers) if numbers else None}
    grouped = {}
    missing_keys = 0
    if key_columns:
        for i, row in enumerate(rows, 2):
            key = tuple(row[k] for k in key_columns)
            if any(x.strip() in missing for x in key):
                missing_keys += 1
                continue
            grouped.setdefault(key, []).append((i, tuple(row[k] for k in fields)))
    conflicts = [{'source_rows': [i for i, _ in items], 'records': len(items)}
                 for items in grouped.values() if len({record for _, record in items}) > 1]
    timing = None
    if time_column:
        parsed, invalid_rows, naive_rows = [], [], []
        for i, row in enumerate(rows, 2):
            try:
                dt = datetime.fromisoformat(row[time_column].replace('Z', '+00:00'))
                if dt.tzinfo is None or dt.utcoffset() is None:
                    naive_rows.append(i)
                else:
                    parsed.append(dt)
            except ValueError:
                invalid_rows.append(i)
        timing = {'valid_offset_times': len(parsed), 'missing_offset_rows': naive_rows,
                  'invalid_or_missing_rows': invalid_rows,
                  'earliest': min(parsed).isoformat() if parsed else None,
                  'latest': max(parsed).isoformat() if parsed else None,
                  'ordering': 'not_evaluated: group by instrument/point before checking order'}
    return {'rows': len(rows), 'columns': columns,
            'exact_duplicate_excess': sum(n-1 for n in fingerprints.values()),
            'key_columns': key_columns, 'missing_key_rows': missing_keys,
            'conflicting_key_groups': conflicts, 'time': timing,
            'missing_tokens': sorted(missing), 'modified_input': False,
            'note': 'Numeric parsing is not a semantic type inference; source_rows are logical CSV record numbers including header.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--missing-token', action='append', default=[])
    parser.add_argument('--key', nargs='*', default=[])
    parser.add_argument('--time-column')
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    try:
        result = profile(a.input, set([''] + a.missing_token), a.key, a.time_column)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        with a.output.open('x', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
