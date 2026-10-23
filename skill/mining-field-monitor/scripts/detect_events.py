"""Screen explicitly supplied upper-threshold rules on offset-aware monitoring data."""
import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
from collections import defaultdict


def positive(value, name, allow_zero=False):
    x = float(value)
    if not math.isfinite(x) or x < 0 or (x == 0 and not allow_zero):
        raise ValueError(f'{name} is out of range.')
    return x


def detect(rows, threshold, operator, max_gap, min_span):
    groups, issues = defaultdict(list), []
    for i, row in enumerate(rows, 2):
        point = row['point_id'].strip()
        if not point:
            raise ValueError(f'Row {i}: point_id is missing.')
        try:
            timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError()
        except ValueError:
            raise ValueError(f'Row {i}: provide a valid ISO timestamp with UTC offset.')
        try:
            value = float(row['value'])
            if not math.isfinite(value):
                raise ValueError()
        except ValueError:
            value = None
            issues.append({'type': 'invalid_or_missing_value', 'point_id': point, 'source_rows': [i]})
        groups[point].append((timestamp, value, i))
    events, coverage = [], {}
    for point, observations in sorted(groups.items()):
        by_time = defaultdict(list)
        for record in observations:
            by_time[record[0]].append(record)
        ordered = []
        for timestamp, records in sorted(by_time.items()):
            if len(records) > 1:
                issues.append({'type': 'duplicate_timestamp', 'point_id': point,
                               'source_rows': [r[2] for r in records]})
                # Preserve ambiguous duplicate instants as a break rather than silently choosing a value.
                ordered.append((timestamp, None, [r[2] for r in records]))
            else:
                ordered.append((timestamp, records[0][1], [records[0][2]]))
        valid = sum(value is not None for _, value, _ in ordered)
        coverage[point] = {'observed_instants': len(ordered), 'valid_instants': valid,
                           'status': 'unavailable' if valid == 0 else 'partially_available' if valid < len(ordered) else 'available'}
        run = []

        def close(reason):
            if not run:
                return
            span = (run[-1][0] - run[0][0]).total_seconds()
            events.append({'event_id': f'E{len(events)+1:04d}', 'point_id': point,
                           'first_observed': run[0][0].isoformat(), 'last_observed': run[-1][0].isoformat(),
                           'sampled_span_seconds': span, 'sample_count': len(run),
                           'peak_value': max(x[1] for x in run), 'source_rows': [i for x in run for i in x[2]],
                           'status': 'sampled_span_met' if span >= min_span else 'point_exceedance_only',
                           'closed_by': reason})
            run.clear()

        previous = None
        for timestamp, value, source_rows in ordered:
            if previous is not None and (timestamp - previous).total_seconds() > max_gap:
                close('gap')
                issues.append({'type': 'gap', 'point_id': point, 'from': previous.isoformat(),
                               'to': timestamp.isoformat(), 'seconds': (timestamp-previous).total_seconds()})
            if value is None:
                close('invalid_or_ambiguous_record')
            elif value >= threshold if operator == 'ge' else value > threshold:
                run.append((timestamp, value, source_rows))
            else:
                close('non_exceeding_observation')
            previous = timestamp
        close('data_end')
    return {'rule': {'threshold': threshold, 'operator': operator, 'max_gap_seconds': max_gap,
                     'minimum_sampled_span_seconds': min_span}, 'events': events, 'quality_issues': issues,
            'point_coverage': coverage,
            'interpretation': 'Sampled runs only. No continuous-signal proof, regulatory risk grade, or automatic equipment action.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--threshold', type=float, required=True)
    parser.add_argument('--operator', choices=['gt', 'ge'], required=True)
    parser.add_argument('--max-gap-seconds', type=float, required=True)
    parser.add_argument('--min-span-seconds', type=float, required=True)
    parser.add_argument('--unit', required=True)
    parser.add_argument('--rule-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    try:
        if not math.isfinite(a.threshold) or not a.unit.strip() or not a.rule_id.strip():
            raise ValueError('A finite threshold, unit and rule ID are required.')
        gap = positive(a.max_gap_seconds, 'max-gap-seconds')
        span = positive(a.min_span_seconds, 'min-span-seconds', allow_zero=True)
        with a.input.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            if len(fields) != len(set(fields)) or not {'point_id', 'timestamp', 'value'} <= set(fields):
                raise ValueError('Need unique point_id, timestamp, value columns.')
            rows = list(reader)
        if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError('Empty or non-rectangular CSV.')
        if 'unit' in fields and any(r['unit'].strip() != a.unit for r in rows):
            raise ValueError('Mixed or missing units: normalize and verify them before screening.')
        result = detect(rows, a.threshold, a.operator, gap, span)
        result['rule'].update({'unit': a.unit, 'rule_id': a.rule_id})
        a.output.parent.mkdir(parents=True, exist_ok=True)
        with a.output.open('x', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
