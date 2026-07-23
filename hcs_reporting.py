"""Portable analysis and HTML reporting for the healthcare simulation.

This module deliberately has no oTree dependency. The live application and
the offline CSV importer both call the same functions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from html import escape
from pathlib import Path


ANALYSIS_VERSION = 'hcs-1'


def make_spec(roles, rounds, test_role_keys):
    """Return the complete, serializable specification used for scoring."""
    return {
        'analysis_version': ANALYSIS_VERSION,
        'roles': roles,
        'rounds': rounds,
        'test_role_keys': list(test_role_keys),
    }


def normalize_spec(spec):
    """Normalize JSON-loaded specifications to the in-memory shape."""
    normalized = dict(spec)
    normalized['rounds'] = {
        int(round_number): round_data
        for round_number, round_data in spec['rounds'].items()
    }
    normalized['test_role_keys'] = tuple(spec['test_role_keys'])
    return normalized


def serialize_spec(spec):
    return json.dumps(
        spec,
        ensure_ascii=False,
        separators=(',', ':'),
        sort_keys=True,
    )


def specification_hash(spec_json):
    return hashlib.sha256(spec_json.encode('utf-8')).hexdigest()


def _role_averages(records, role_keys):
    values_by_role = {role_key: [] for role_key in role_keys}
    for record in records:
        choice = record.get('impact_choice')
        role_key = record.get('role_key')
        if choice is not None and role_key in values_by_role:
            values_by_role[role_key].append(choice)
    return {
        role_key: sum(values) / len(values)
        for role_key, values in values_by_role.items()
        if values
    }


def calculate_metrics_by_round(records, through_round, spec, test_mode=False):
    """Calculate every metric through ``through_round`` from plain records."""
    spec = normalize_spec(spec)
    roles = spec['roles']
    role_by_key = {role['key']: role for role in roles}
    role_keys = set(role_by_key)
    records_by_round = defaultdict(list)
    for record in records:
        records_by_round[int(record['round'])].append(record)

    assumed_neutral = (
        role_keys - set(spec['test_role_keys']) if test_mode else set()
    )
    metrics_by_round = {}

    for round_number in range(1, through_round + 1):
        role_averages = _role_averages(
            records_by_round[round_number], role_keys
        )
        scoring_averages = {
            role_key: 3 for role_key in assumed_neutral
        }
        scoring_averages.update(role_averages)
        previous = {
            prior_round: {
                metric['key']: metric
                for metric in metrics_by_round[prior_round]
            }
            for prior_round in range(1, round_number)
        }

        metrics = []
        for definition in spec['rounds'][round_number]['metrics']:
            effects = {
                role_key: effect
                for role_key, effect in definition['effects'].items()
                if role_key in scoring_averages
            }
            weight_total = sum(abs(effect) for effect in effects.values())
            vote_numerator = sum(
                effect * ((scoring_averages[role_key] - 3) / 2)
                for role_key, effect in effects.items()
            )
            vote_effect = (
                25 * vote_numerator / weight_total if weight_total else 0
            )

            carryover_effect = 0
            carryover_rows = []
            for source_round, source_key, coefficient in definition[
                'carryovers'
            ]:
                source = previous[int(source_round)][source_key]
                effect = coefficient * (source['value'] - 50)
                carryover_effect += effect
                carryover_rows.append(
                    {
                        'round_number': int(source_round),
                        'name': source['name'],
                        'value': source['display_value'],
                        'coefficient': coefficient,
                        'effect': round(effect, 1),
                        'calculation': (
                            '{coefficient:g} × ({value:.1f} − 50) = '
                            '{effect:+.1f}'
                        ).format(
                            coefficient=coefficient,
                            value=source['value'],
                            effect=effect,
                        ),
                    }
                )

            raw_value = 50 + vote_effect + carryover_effect
            value = round(max(0, min(100, raw_value)), 1)
            contributors = []
            for role_key, effect in effects.items():
                role_mean = scoring_averages[role_key]
                contribution = (
                    25
                    * effect
                    * ((role_mean - 3) / 2)
                    / weight_total
                )
                contributors.append(
                    {
                        'name': role_by_key[role_key]['name'],
                        'mean': round(role_mean, 2),
                        'weight': effect,
                        'contribution': round(contribution, 1),
                        'assumed_neutral': role_key in assumed_neutral,
                    }
                )

            previous_explanation = (
                'Earlier scores shift the 50-point baseline using the '
                'carry-over terms below. A prior score of 50 has no effect.'
                if carryover_rows
                else 'This is the opening round, so no previous result '
                'influences this metric.'
            )
            metrics.append(
                {
                    'key': definition['key'],
                    'name': definition['name'],
                    'short': definition['short'],
                    'color': definition['color'],
                    'explanation': definition['explanation'],
                    'value': value,
                    'display_value': (
                        value if effects or carryover_rows else '—'
                    ),
                    'vote_effect': round(vote_effect, 1),
                    'carryover_effect': round(carryover_effect, 1),
                    'calculation': (
                        '50 {vote:+.1f} from this round '
                        '{carry:+.1f} carried forward = {value:.1f}'
                    ).format(
                        vote=vote_effect,
                        carry=carryover_effect,
                        value=value,
                    ),
                    'formula': (
                        'Score = clamp(50 + 25 × '
                        '[Σ(weight × (role mean − 3) ÷ 2) ÷ Σ|weight|] '
                        '+ Σ[coefficient × (prior score − 50)], 0, 100)'
                    ),
                    'previous_explanation': previous_explanation,
                    'carryovers': carryover_rows,
                    'contributors': contributors,
                    'represented_count': sum(
                        role_key in role_averages for role_key in effects
                    ),
                    'assumed_neutral_count': sum(
                        role_key in assumed_neutral for role_key in effects
                    ),
                }
            )
        metrics_by_round[round_number] = metrics

    return metrics_by_round


def build_reports(records, through_round, spec, test_mode=False, role_key=None):
    spec = normalize_spec(spec)
    metrics_by_round = calculate_metrics_by_round(
        records, through_round, spec, test_mode
    )
    reports = []
    for round_number in range(1, through_round + 1):
        round_data = spec['rounds'][round_number]
        reports.append(
            {
                'round_number': round_number,
                'title': round_data['title'],
                'short': round_data['short'],
                'question': (
                    round_data['questions'][role_key] if role_key else None
                ),
                'metrics': metrics_by_round[round_number],
            }
        )
    return reports


def build_role_rows(records, round_number, spec, test_mode=False):
    spec = normalize_spec(spec)
    roles = spec['roles']
    round_records = [
        record for record in records if int(record['round']) == round_number
    ]
    role_averages = _role_averages(
        round_records, {role['key'] for role in roles}
    )
    assumed_neutral = (
        {role['key'] for role in roles} - set(spec['test_role_keys'])
        if test_mode
        else set()
    )
    rows = []
    for role in roles:
        role_key = role['key']
        average = role_averages.get(role_key)
        is_assumed_neutral = role_key in assumed_neutral
        rows.append(
            {
                'name': role['name'],
                'question': spec['rounds'][round_number]['questions'][
                    role_key
                ],
                'n': sum(
                    record.get('role_key') == role_key
                    and record.get('impact_choice') is not None
                    for record in round_records
                ),
                'mean': (
                    3
                    if is_assumed_neutral
                    else round(average, 2)
                    if average is not None
                    else '—'
                ),
                'basis': (
                    'Non-participating; assumed neutral'
                    if is_assumed_neutral
                    else 'Participant response'
                    if average is not None
                    else 'No response'
                ),
            }
        )
    return rows


def _select_session(rows, session_field, session_code):
    available_sessions = sorted(
        {row[session_field] for row in rows if row.get(session_field)}
    )
    if session_code is None:
        if len(available_sessions) != 1:
            raise ValueError(
                'The export contains multiple sessions; choose one with '
                '--session. Available: ' + ', '.join(available_sessions)
            )
        session_code = available_sessions[0]
    selected = [
        row for row in rows if row.get(session_field) == session_code
    ]
    if not selected:
        raise ValueError(f'Session {session_code!r} is not in the export.')
    return session_code, selected


def _load_spec_metadata(selected, fields):
    versions = {row[fields['version']] for row in selected}
    modes = {row[fields['test_mode']].strip().lower() for row in selected}
    hashes = {row[fields['spec_hash']] for row in selected}
    specs = {row[fields['spec_json']] for row in selected}
    if (
        len(versions) != 1
        or len(modes) != 1
        or len(hashes) != 1
        or len(specs) != 1
    ):
        raise ValueError(
            'The selected session has inconsistent report metadata.'
        )
    if versions != {ANALYSIS_VERSION}:
        raise ValueError(
            'Unsupported analysis version: ' + ', '.join(sorted(versions))
        )

    spec_json = specs.pop()
    expected_hash = hashes.pop()
    if specification_hash(spec_json) != expected_hash:
        raise ValueError('The embedded analysis specification hash is invalid.')
    spec = normalize_spec(json.loads(spec_json))
    if spec.get('analysis_version') != ANALYSIS_VERSION:
        raise ValueError('The embedded specification version is unsupported.')
    test_mode = modes.pop() in {'1', 'true', 'yes'}
    return spec, expected_hash, test_mode


def _validate_records(records, spec):
    present_rounds = {record['round'] for record in records}
    expected_rounds = set(range(1, max(spec['rounds']) + 1))
    if not expected_rounds.issubset(present_rounds):
        raise ValueError(
            'The export is incomplete; expected rounds '
            + ', '.join(map(str, sorted(expected_rounds)))
        )


def _parse_choice(choice_text):
    choice_text = choice_text.strip()
    choice = int(choice_text) if choice_text else None
    if choice is not None and choice not in range(1, 6):
        raise ValueError(f'Invalid impact_choice {choice!r}.')
    return choice


def _latest_complete_wide_session(rows):
    """Choose the most recently started complete healthcare session."""
    rows_by_session = defaultdict(list)
    for row in rows:
        session_code = row.get('session.code', '')
        if session_code:
            rows_by_session[session_code].append(row)

    candidates = []
    for session_code, session_rows in rows_by_session.items():
        spec_json = session_rows[0].get(
            'session.hcs_analysis_spec_json', ''
        )
        if not spec_json:
            continue
        try:
            spec = normalize_spec(json.loads(spec_json))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
        complete = all(
            row.get(
                f'health_survey.{round_number}.player.stakeholder_role', ''
            ).strip()
            and row.get(
                f'health_survey.{round_number}.player.impact_choice', ''
            ).strip()
            for row in session_rows
            for round_number in spec['rounds']
        )
        if complete:
            latest_start = max(
                row.get('participant.time_started_utc', '')
                for row in session_rows
            )
            candidates.append((latest_start, session_code))

    if not candidates:
        raise ValueError(
            'The export contains no complete three-round healthcare session.'
        )
    return max(candidates)[1]


def _load_wide_export(rows, session_code):
    metadata_fields = {
        'version': 'session.hcs_analysis_version',
        'test_mode': 'session.config.test_mode',
        'spec_hash': 'session.hcs_analysis_spec_hash',
        'spec_json': 'session.hcs_analysis_spec_json',
    }
    required = {'session.code', 'participant.code', *metadata_fields.values()}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(
            'This standard oTree export predates portable reporting; missing '
            'columns: ' + ', '.join(sorted(missing))
        )

    if session_code is None:
        session_code = _latest_complete_wide_session(rows)
    session_code, selected = _select_session(
        rows, 'session.code', session_code
    )
    spec, expected_hash, test_mode = _load_spec_metadata(
        selected, metadata_fields
    )

    records = []
    for row in selected:
        for round_number in range(1, max(spec['rounds']) + 1):
            prefix = f'health_survey.{round_number}.player.'
            role_field = prefix + 'stakeholder_role'
            choice_field = prefix + 'impact_choice'
            if role_field not in row or choice_field not in row:
                raise ValueError(
                    'The standard oTree export is missing healthcare fields '
                    f'for round {round_number}.'
                )
            role_key = row[role_field].strip()
            if not role_key:
                continue
            records.append(
                {
                    'round': round_number,
                    'role_key': role_key,
                    'impact_choice': _parse_choice(row[choice_field]),
                    'participant_code': row['participant.code'],
                }
            )

    _validate_records(records, spec)
    return {
        'session_code': session_code,
        'test_mode': test_mode,
        'spec': spec,
        'spec_hash': expected_hash,
        'records': records,
    }


def load_export(path, session_code=None):
    """Load a standard oTree all-apps-wide CSV."""
    with Path(path).open('r', encoding='utf-8-sig', newline='') as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError('The export contains no result rows.')
    if 'session.code' not in rows[0]:
        raise ValueError(
            'Unsupported CSV layout. Download "All apps (wide format)" '
            'from oTree.'
        )
    return _load_wide_export(rows, session_code)


REPORT_CSS = """
body{color:#294e56;font-family:Arial,sans-serif;margin:0;background:#f7f9f9}
main{max-width:1100px;margin:0 auto;padding:32px 20px}
h1{color:#183f46}.intro{color:#455b60;max-width:800px}
.round{background:#fff;border:1px solid #dce4e5;border-radius:12px;margin:24px 0;overflow:hidden}
.round>header{background:#eef4f4;padding:16px 20px}.round h2{margin:0 0 4px}
.round>header p{margin:0;color:#5d7377}.question{border-left:4px solid #8aa7ac;margin:16px 20px 0;padding:9px 13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:18px;margin:20px}
.card{border:1px solid #dce4e5;border-top:5px solid var(--color);border-radius:12px;padding:19px}
.number{color:#183f46;font-size:32px;font-weight:800}.card h3{margin:3px 0}.summary{color:#65777b;min-height:42px}
.bar{background:#e8eeee;border-radius:999px;height:10px;overflow:hidden}.fill{background:var(--color);height:100%}
details{border-top:1px solid #e3e9ea;margin-top:16px;padding-top:13px}summary{cursor:pointer;font-weight:700}
details p,details li{color:#5c6f73;font-size:13px;line-height:1.45}
.formula{background:#f4f7f7;border-radius:7px;display:block;font-family:monospace;font-size:12px;padding:10px}
.meta{color:#667b7f;font-size:12px;margin-top:24px}
"""


def render_report_html(bundle, role_key=None):
    """Render a self-contained cumulative round-3 report."""
    spec = normalize_spec(bundle['spec'])
    role_by_key = {role['key']: role for role in spec['roles']}
    if role_key is not None and role_key not in role_by_key:
        raise ValueError(f'Unknown role key {role_key!r}.')
    final_round = max(spec['rounds'])
    reports = build_reports(
        bundle['records'],
        final_round,
        spec,
        bundle['test_mode'],
        role_key,
    )

    sections = []
    for report in reports:
        cards = []
        for metric in report['metrics']:
            carryovers = ''.join(
                '<li>Round {round_number} {name}: {calculation}</li>'.format(
                    **{key: escape(str(value)) for key, value in item.items()}
                )
                for item in metric['carryovers']
            )
            contributors = ''.join(
                '<li>{name}: mean {mean}, weight {weight}, contribution '
                '{contribution}{neutral}</li>'.format(
                    name=escape(item['name']),
                    mean=item['mean'],
                    weight=item['weight'],
                    contribution=item['contribution'],
                    neutral=' (assumed neutral)'
                    if item['assumed_neutral']
                    else '',
                )
                for item in metric['contributors']
            )
            cards.append(
                f"""
                <article class="card" style="--color:{escape(metric['color'])}">
                  <div class="number">{metric['display_value']}</div>
                  <h3>{escape(metric['name'])}</h3>
                  <p class="summary">{escape(metric['short'])}</p>
                  <div class="bar"><div class="fill" style="width:{metric['value']}%"></div></div>
                  <details><summary>How this metric was calculated</summary>
                    <p>{escape(metric['explanation'])}</p>
                    <span class="formula">{escape(metric['formula'])}</span>
                    <p><strong>This result:</strong> {escape(metric['calculation'])}</p>
                    <p><strong>Influence of previous rounds:</strong> {escape(metric['previous_explanation'])}</p>
                    {'<ul>' + carryovers + '</ul>' if carryovers else ''}
                    <p><strong>Influence of this round’s role votes:</strong></p>
                    <ul>{contributors}</ul>
                  </details>
                </article>"""
            )
        question_html = ''
        if role_key is not None:
            question_html = (
                '<p class="question"><strong>Your {role} question was:'
                '</strong> {question}</p>'
            ).format(
                role=escape(role_by_key[role_key]['name']),
                question=escape(report['question']),
            )
        sections.append(
            f"""
            <section class="round">
              <header><h2>Round {report['round_number']} · {escape(report['title'])}</h2>
                <p>{escape(report['short'])}</p></header>
              {question_html}
              <div class="grid">{''.join(cards)}</div>
            </section>"""
        )

    mode_note = (
        ' Test mode: non-participating roles were treated as neutral.'
        if bundle['test_mode']
        else ''
    )
    role_meta = (
        ' · Role ' + escape(role_by_key[role_key]['name'])
        if role_key is not None
        else ''
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Healthcare simulation final report</title><style>{REPORT_CSS}</style></head>
<body><main><h1>Healthcare simulation final report</h1>
<p class="intro">This report contains every completed round. Scores are out of
100; 50 is neutral, and decisions accumulate through the carry-over terms.
{escape(mode_note)}</p>{''.join(sections)}
<p class="meta">Session {escape(bundle['session_code'])}{role_meta} ·
Analysis {ANALYSIS_VERSION} ·
Specification {escape(bundle['spec_hash'])}</p></main></body></html>"""


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Regenerate a healthcare simulation report from CSV.'
    )
    parser.add_argument(
        'csv_file',
        help='oTree all-apps-wide CSV',
    )
    parser.add_argument('--session', help='Session code when CSV has several')
    parser.add_argument('--role', help='Stakeholder role key')
    parser.add_argument(
        '--output', default='healthcare-final-report.html', help='Output HTML'
    )
    args = parser.parse_args(argv)
    try:
        bundle = load_export(args.csv_file, args.session)
        report_html = render_report_html(bundle, args.role)
        output = Path(args.output)
        output.write_text(report_html, encoding='utf-8')
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    detail = f' and role {args.role}' if args.role else ''
    print(
        f"Wrote {output} for session {bundle['session_code']}{detail}."
    )


if __name__ == '__main__':
    main()
