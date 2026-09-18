# Personal Chef

Personal Chef is a repository-backed workflow for an AI meal-planning and grocery-shopping agent. It turns preferences into a recipe menu, scales selected meals to six servings, builds comparable Food Lion and Instacart carts, pauses for approval, and records what happened so future runs improve.

## Start here

1. Read [`AGENTS.md`](AGENTS.md) for the short operating contract and document map.
2. Read [`docs/DESIGN.md`](docs/DESIGN.md) for the product intent and authority model.
3. Update [`registers/preferences.yaml`](registers/preferences.yaml) when durable tastes or constraints change.
4. Copy [`local/private.example.yaml`](local/private.example.yaml) to `local/private.yaml` for private delivery details. The real file is ignored by Git.
5. Start each practical new-chat request from [`templates/session.yaml`](templates/session.yaml), then create and link a run from [`templates/run.yaml`](templates/run.yaml) when the request enters a menu/cart/order cycle.
6. Validate changes with `python scripts/validate.py` and the relevant checks in [`docs/QUALITY.md`](docs/QUALITY.md).

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Short agent entry point and map to the sources of truth |
| `docs/DESIGN.md` | Product intent, authority boundaries, system model, and design decisions |
| `docs/WORKFLOW.md` | Detailed meal-to-order operating sequence |
| `docs/QUALITY.md` | Acceptance criteria and verification layers |
| `docs/REGISTER_REFERENCE.md` | Data ownership, evidence, and freshness rules |
| `docs/OPERATIONS.md` | Repository maintenance procedures |
| `registers/` | Durable preferences, retailer facts, availability, substitutions, outcomes, issues, and change history |
| `recipes/` | Versioned recipe records with scaling and nutrition metadata |
| `runs/` | One auditable record per menu/cart/order cycle |
| `sessions/` | One concise encounter record per practical chat request, linking work, lessons, and follow-up |
| `templates/` | Copyable YAML records for new sessions, recipes, menus, and runs |
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

The first validated recipe is [`recipes/instant-pot-lemon-chicken-white-bean-kale-stew.yaml`](recipes/instant-pot-lemon-chicken-white-bean-kale-stew.yaml). The recipe library contains only meals that were cooked and positively evaluated by the user.
