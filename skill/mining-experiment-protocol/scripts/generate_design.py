"""Generate a seeded full-factorial run schedule from explicit factor levels."""
import argparse
import csv
import itertools
import json
import math
from pathlib import Path
import random


def generate(config):
    factors = config.get('factors')
    if not isinstance(factors, dict) or not factors:
        raise ValueError('factors must be a non-empty object of factor: [levels].')
    reserved = {'run_id', 'block', 'replicate'}
    for name, levels in factors.items():
        if not name.strip() or name in reserved:
            raise ValueError(f'Invalid or reserved factor name: {name}')
        if not isinstance(levels, list) or len(levels) < 2:
            raise ValueError(f'{name}: supply at least two explicit levels.')
        if any(isinstance(x, (dict, list, bool)) or x is None for x in levels):
            raise ValueError(f'{name}: levels must be strings or numbers.')
        if any(isinstance(x, float) and not math.isfinite(x) for x in levels):
            raise ValueError(f'{name}: levels must be finite.')
        if len({str(x) for x in levels}) != len(levels):
            raise ValueError(f'{name}: duplicate levels.')
    repeats = config.get('replicates', 1)
    if type(repeats) is not int or repeats < 1:
        raise ValueError('replicates must be a positive integer.')
    blocks = config.get('blocks', ['all'])
    if not isinstance(blocks, list) or not blocks or any(not isinstance(x, str) or not x.strip() for x in blocks):
        raise ValueError('blocks must contain non-empty strings.')
    if len(blocks) != len(set(blocks)):
        raise ValueError('Duplicate block labels.')
    count = math.prod(len(x) for x in factors.values()) * repeats * len(blocks)
    if count > 100000:
        raise ValueError('More than 100000 runs: reduce the design or use a dedicated DOE tool.')
    seed = config.get('seed')
    if type(seed) is not int:
        raise ValueError('Supply an integer seed to reproduce the run order.')
    rng = random.Random(seed)
    result = []
    for block in blocks:
        rows = []
        for replicate in range(1, repeats + 1):
            for values in itertools.product(*factors.values()):
                rows.append({'block': block, 'replicate': replicate, **dict(zip(factors, values))})
        rng.shuffle(rows)
        for row in rows:
            result.append({'run_id': len(result) + 1, **row})
    return result, ['run_id', 'block', 'replicate', *factors]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        rows, fields = generate(json.loads(args.config.read_text(encoding='utf-8-sig')))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            writer.writerows(rows)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')
    print(f'Created {len(rows)} planned runs. Replication labels do not establish independent specimens.')


if __name__ == '__main__':
    main()
