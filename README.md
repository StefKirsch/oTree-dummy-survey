# Healthcare-system stakeholder simulation

This oTree proof of concept assigns participants one of 11 healthcare-system
stakeholder roles. Each role receives a tailored Likert statement. After all
participants answer, three aggregate impact plots show system alignment,
accessible care, and innovation readiness on a 0–100 scale.

For 11 participants, each role is assigned once. In larger sessions the role
sequence repeats. The shared `System alignment` metric includes all roles; the
other two metrics use role subsets and explicit weights. Questions and weights
are defined near the top of `health_survey/__init__.py`.

Two session configurations make it easy to switch modes from oTree's demo or
session-creation page:

- `Healthcare System Stakeholder Simulation` is the full 11-role mode.
- `Healthcare System Stakeholder Simulation (3-role test mode)` assigns only
  Doctors, Patients, and MedTech. The other eight roles are included in result
  calculations as `3 – Neither agree nor disagree`.

For this project to run you need [Python 3.12](https://conda-forge.org/download/) and [uv](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2) installed.

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Run the survey on a local server

```bash
uv run otree devserver
```

### 3. Open survey in your browser

Navigate to [http://localhost:8000/](http://localhost:8000/).
