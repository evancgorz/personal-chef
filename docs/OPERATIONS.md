# Operations guide

## Starting a run

Copy `templates/run.yaml` to `runs/YYYY-MM-DD-short-description.yaml`, create a unique run ID, set `status: draft`, and add the user's request under `request`.

## Adding a recipe

Copy `templates/recipe.yaml` into `recipes/<recipe-id>.yaml`. Include canonical yield, timing, equipment, instructions, ingredient amounts, nutrition estimates, effort notes, and tags. Validate before offering it.

## Recording availability

Append a store observation to `registers/availability.yaml`. Use an exact product name and package size when visible. Record `null` for an unknown price rather than estimating it. Refresh the observation during the next shopping run.

## Resolving an issue

Keep the issue record. Change its status to `resolved`, add `resolved_at`, and describe the mitigation. If the mitigation changes the operating contract or a durable preference, add an entry to the change log.

## Private configuration

Copy `local/private.example.yaml` to `local/private.yaml`. Keep address, phone, email, account labels, and delivery notes there. Use references such as `home` in tracked run files instead of copying private values.

## Validation

Install the optional development dependency and validate:

```text
python -m pip install -r requirements-dev.txt
python scripts/validate.py
```

CI runs the same validation for pushes and pull requests.

