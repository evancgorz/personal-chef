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
- `sessions/*.yaml`: one concise record per practical chat request, linking intent, runs, issues, changes, outcomes, artifacts, lessons, and follow-up.
- `local/receipts/`: ignored original receipt artifacts that may contain private account, address, or payment fields; tracked runs contain only sanitized receipt facts.

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

## Register ownership

| Register | Write when | Do not write when |
| --- | --- | --- |
| `preferences.yaml` | The user states a durable preference or approves a proposed change | A single recipe succeeds or an item is temporarily unavailable |
| `retailers.yaml` | Store, channel, capability, or selection policy changes | A transient price changes |
| `pantry.yaml` | Quantity is explicitly reported or verified | Quantity is assumed from a prior order |
| `availability.yaml` | Product, price, package, and channel are directly observed | A product is merely suggested or remembered |
| `substitutions.yaml` | A substitution is approved, rejected, or evaluated | The agent only considers an alternative |
| `outcomes.yaml` | The meal is cooked or the user supplies feedback; an unresolved final form may reference the candidate ID from its run | A cart is built but the meal is not evaluated |
| `issues.yaml` | A workflow failure or recurring friction is observed | A normal approval gate is reached |
| `change-log.yaml` | Any durable tracked policy or design change occurs | Only a volatile run file changes |
| `sessions/*.yaml` | A new practical chat request begins; update it at meaningful milestones and close it with a concise retrospective | Raw chat text, private fields, or duplicated cart and receipt details |

## Data integrity

- IDs are stable lowercase kebab-case.
- Dates and timestamps use ISO 8601.
- Money uses a numeric decimal value plus a three-letter currency code.
- Unknown values are `null`, never invented.
- Observed prices and availability retain their source and observation time.
- Historical runs are append-only records of what happened; corrections supersede rather than rewrite history.
- Historical sessions are append-only encounter summaries. Add corrections or closing facts without rewriting the original chronology.
- Session summaries link to authoritative run and register IDs instead of duplicating their detailed facts.
- Private addresses and credentials never enter tracked files.
- Receipt originals with private fields remain untracked; their sanitized run records omit addresses, contact information, payment details, and authentication data.
