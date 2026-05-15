# CLAUDE.md

This file gives Claude Code style guidance for working in this repository.

## Project at a glance

- Framework: Django
- Domain: retirement and savings forecasting with stochastic scenario generation
- Core app logic: pages app
- Main simulation entry point: stochastic_finances_func.main

## Environment and setup

Python target is 3.10+ (Poetry config). This repo has some legacy docs for older Python versions, so prefer Poetry settings when in doubt.

Typical setup:

```bash
poetry install
poetry shell
python manage.py migrate
python manage.py runserver
```

Alternative setup (if using pip):

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Common commands

Run Django tests:

```bash
python manage.py test
```

Run pytest suite (configured to use Django settings):

```bash
pytest
```

Lint and format Python:

```bash
ruff check .
ruff check --fix .
ruff format .
```

Lint and format Django templates:

```bash
djlint templates --check
djlint templates --reformat
```

## High-value code locations

- pages/base_scenario.py: deterministic monthly/yearly timeline math
- pages/random_scenario.py: stochastic perturbations and variable scenario logic
- pages/views.py: active-input collection and calculations flow
- pages/models.py: persisted input models used to build assumptions
- tests/: pytest-based tests for stochastic_finances_func behavior

## Data and outputs

- Input assumption examples: input_assumptions_*.json
- Generated scenario CSV outputs: outputs/
- Healthcare research inputs: research/healthcare/

## Working conventions

- Keep financial logic deterministic unless explicitly modifying stochastic behavior.
- Use explicit, scenario-based tests for regressions in rates, inflation, withdrawals, and aggregation math.
- Prefer small, focused changes and avoid broad refactors unless requested.
- Do not modify generated outputs in outputs/ unless the task specifically requires output regeneration.

## Testing guidance for contributors

- Use fast, focused unit tests for pure calculation behavior.
- Add regression tests when fixing bugs in interest-rate handling, retirement cash flow, or aggregate outputs.
- Validate edge cases around age boundaries (59y6m, 65, RMD ages) and month transitions.

## Notes for AI coding agents

- Keep assumptions shape compatibility when passing dictionaries into scenario constructors.
- Preserve existing column names in DataFrame outputs unless a migration/update is requested.
- When changing calculations-tab behavior, verify parity against stochastic CSV scenario outputs and update tests accordingly.
- For GitHub issue/PR updates or comments, prefer MCP GitHub tools directly (for example: add issue comment/review comment tools) instead of terminal-based gh commands unless MCP is unavailable.
