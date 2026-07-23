# Healthcare-system stakeholder simulation

This oTree proof of concept is a synchronized, three-round policy game for 11
healthcare stakeholder roles:

1. Cost and financial burden
2. Wait times, access, and medical-staff workload
3. Quality and coverage of care

Every role receives a different trade-off question in every round. Answers use
a 1–5 agreement scale. Once a participant submits, a wait page prevents the
session from continuing until every stakeholder has submitted that round.
Everyone then sees the same report with three metrics.

Round 1 scores are based on the stakeholder votes. In rounds 2 and 3, every
score is calculated as:

`50 + current-round vote effect + weighted earlier-round deviations from 50`

The report gives a short substantive explanation, the exact carry-over terms,
and each role's contribution for every metric. Previous reports also appear
above the current-round question.

Questions, metric weights, and carry-over coefficients are defined in
`health_survey/__init__.py`.

## Portable final reports

The scoring implementation is in `hcs_reporting.py` and has no oTree
dependency. The live application passes plain response records to this module.
When a session is created, its complete versioned analysis specification is
frozen on the session so that later code changes cannot alter its calculations.

oTree's standard **all apps (wide)** CSV contains the raw responses, session
mode, analysis version, specification hash, and a copy of the frozen
specification. A round-3 participant can also use **Download this report** to
save their cumulative report as a self-contained HTML file.

To regenerate a role-neutral report later:

```bash
python hcs_reporting.py all_apps_wide-2026-07-23.csv \
    --output final-report.html
```

Without `--session`, the most recently started complete three-round healthcare
session is selected from the CSV. Use `--session` only to override that choice.
Use `--role` only when a role-personalized report, including that role's
questions, is wanted. The importer validates the embedded specification hash
and refuses incomplete three-round exports.

## Persistent participant links

The `Classroom` room uses the role names in `_rooms/classroom.txt`. Its labeled
room URLs are reusable: reopening the same URL returns a participant to their
current page. Each full-session room label also fixes that participant's role,
regardless of the order in which people join. Create a session for the room
from oTree's Rooms page and distribute one labeled URL per stakeholder.

The ordinary session and demo links still work for quick testing, but a labeled
room is the intended setup for a live exercise.

## Session configurations

- `Healthcare System Stakeholder Simulation`: all 11 roles.
- `Healthcare System Stakeholder Simulation (3-role test mode)`: Doctors,
  Patients, and MedTech. Other roles are included as neutral votes.

## Setup

Python 3.12 and [uv](https://docs.astral.sh/uv/) are required.

```bash
uv sync
uv run otree devserver
```

Then open <http://localhost:8000/>.
