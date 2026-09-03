# Personal Chef

Personal Chef is a repository-backed workflow for an AI meal-planning and grocery-shopping agent. It turns preferences into a recipe menu, scales selected meals to six servings, builds comparable Food Lion and Instacart carts, pauses for approval, and records what happened so future runs improve.

## Start here

1. Read [`AGENTS.md`](AGENTS.md) for the authoritative operating contract.
2. Update [`registers/preferences.yaml`](registers/preferences.yaml) when durable tastes or constraints change.
3. Copy [`local/private.example.yaml`](local/private.example.yaml) to `local/private.yaml` for private delivery details. The real file is ignored by Git.
4. Start a run from [`templates/run.yaml`](templates/run.yaml) and save it under `runs/YYYY-MM-DD-slug.yaml`.
5. Validate changes with `python scripts/validate.py`.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Agent rules, workflow, safety gates, and write-back policy |
| `docs/` | Detailed operating and data-model guidance |
| `registers/` | Durable preferences, retailer facts, availability, substitutions, outcomes, issues, and change history |
| `recipes/` | Versioned recipe records with scaling and nutrition metadata |
| `runs/` | One auditable record per menu/cart/order cycle |
| `templates/` | Copyable YAML records for new recipes, menus, and runs |
| `local/` | Private machine-local configuration; real values are not committed |
| `scripts/validate.py` | Structural and cross-reference validation |

## Current baseline

- Six servings per selected meal.
- Most recipes under 45 minutes.
- High protein and vegetable-forward.
- Carb-heavy bases only occasionally.
- Prefer low-prep ingredients, Nature's Promise, and Food Lion brands.
- Prefer grass-fed beef.
- Compare pickup and delivery totals before checkout.

The first recorded recipe is [`recipes/garlic-herb-chicken.yaml`](recipes/garlic-herb-chicken.yaml). Historical pilot pricing is retained in the outcomes register and should never be treated as current availability or price.
