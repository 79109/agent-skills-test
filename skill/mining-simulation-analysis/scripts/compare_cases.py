"""Compare completed one-factor scenarios with an explicitly named baseline."""
import argparse
import csv
import json
import math
from pathlib import Path


def number(value):
    x = float(value)
    if not math.isfinite(x):
        raise ValueError('Non-finite value.')
    return x


def compare(rows, baseline_id, parameters, metrics):
    identifiers = [r['case_id'] for r in rows]
    if any(not x.strip() for x in identifiers) or len(identifiers) != len(set(identifiers)):
        raise ValueError('case_id must be populated and unique.')
    bases = [r for r in rows if r['case_id'] == baseline_id]
    if len(bases) != 1 or bases[0]['status'] != 'completed':
        raise ValueError('Baseline must exist and have status completed.')
    base = bases[0]
    base_values = {key: number(base[key]) for key in parameters + metrics}
    result = []
    for row in rows:
        if row['case_id'] == baseline_id:
            continue
        item = {'case_id': row['case_id'], 'input_status': row['status']}
        if row['status'] != 'completed':
            item['comparison_status'] = 'not_completed'
            result.append(item)
            continue
        try:
            values = {key: number(row[key]) for key in parameters + metrics}
        except (ValueError, TypeError):
            item['comparison_status'] = 'missing_or_invalid_number'
            result.append(item)
            continue
        changed = [p for p in parameters if values[p] != base_values[p]]
        item['changed_parameters'] = changed
        item['metric_deltas'] = {m: values[m] - base_values[m] for m in metrics}
        item['comparison_status'] = 'one_factor' if len(changed) == 1 else 'multiple_factors' if changed else 'no_parameter_change'
        if len(changed) == 1:
            p = changed[0]
            delta = values[p] - base_values[p]
            item['parameter_delta'] = delta
            item['local_slopes'] = {m: (values[m] - base_values[m]) / delta for m in metrics}
            item['elasticities'] = {
                m: ((values[m] - base_values[m]) / delta) * base_values[p] / base_values[m]
                if base_values[p] != 0 and base_values[m] != 0 else None for m in metrics}
        result.append(item)
    return {'baseline': baseline_id, 'parameters': parameters, 'metrics': metrics, 'cases': result,
            'scope': 'Differences on the supplied comparable cases; no solver execution or causal identification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--parameters', nargs='+', required=True)
    parser.add_argument('--metrics', nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    try:
        keys = a.parameters + a.metrics
        if len(keys) != len(set(keys)) or {'case_id', 'status'} & set(keys):
            raise ValueError('Parameter and metric names must be distinct and cannot be case_id/status.')
        with a.input.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            if len(headers) != len(set(headers)) or not set(['case_id', 'status'] + keys) <= set(headers):
                raise ValueError('Required or unique column names are missing.')
            rows = list(reader)
        if any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError('Non-rectangular CSV.')
        result = compare(rows, a.baseline, a.parameters, a.metrics)
        serialized = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        with a.output.open('x', encoding='utf-8') as f:
            f.write(serialized)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
