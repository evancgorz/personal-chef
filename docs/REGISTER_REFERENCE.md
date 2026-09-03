# Register reference

Registers are deliberately separated by volatility and evidence type.

## Durable registers

- `preferences.yaml`: confirmed defaults, tastes, constraints, and scoring targets.
- `retailers.yaml`: preferred stores, brands, channels, and fulfillment capabilities.
- `substitutions.yaml`: ingredient/product substitutions and their approval history.

## Operational registers

- `pantry.yaml`: on-hand quantities with confidence and check dates.
- `availability.yaml`: time-sensitive store observations. Entries expire; they do not become preferences.
- `issues.yaml`: open and resolved workflow problems with mitigations.

## Historical registers

- `outcomes.yaml`: cooked-meal results and user feedback.
- `change-log.yaml`: append-only audit trail for durable register changes.
- `runs/*.yaml`: complete records of menu, carts, approval, order status, and closeout.

## Confidence values

- `verified`: directly observed or explicitly confirmed.
- `reported`: supplied by the user but not independently checked.
- `inferred`: a working assumption that must be labeled.
- `stale`: formerly valid but no longer safe for decisions.

## Freshness defaults

- Availability and price: refresh for every order run.
- Pantry perishables: verify after 3 days.
- Pantry shelf-stable goods: verify after 30 days.
- Retailer capabilities: verify after 90 days or after a failed attempt.
- Preferences: remain active until superseded.

