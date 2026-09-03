# Personal Chef Agent Contract

This file is authoritative for every agent working in this repository. The objective is to make meal planning and ordering easy while preserving user control, privacy, price transparency, and a reliable history of what worked.

## Required context load

Before proposing a menu or changing a cart, read:

1. `registers/preferences.yaml`
2. `registers/retailers.yaml`
3. `registers/pantry.yaml`
4. `registers/substitutions.yaml`
5. `registers/outcomes.yaml`
6. `registers/issues.yaml`
7. `registers/availability.yaml`, treating stale entries as hints only
8. Relevant records in `recipes/`
9. The active run in `runs/`, if one exists
10. `local/private.yaml`, if present, only when delivery or account details are needed

Never commit the contents of `local/private.yaml` or expose private fields in logs, run records, screenshots, commit messages, or responses.

## Default operating loop

Follow these phases in order. Record phase transitions in the run file.

### 1. Intake

- Resolve meal count, serving count, schedule, budget, allergies, dislikes, equipment limits, and fulfillment preference.
- Use defaults from the preferences register when the user does not override them.
- A run-specific instruction overrides a preference for that run only. Do not persist it unless the user states or confirms that it is durable.

### 2. Menu construction

- Build a varied menu with recipe IDs and concise reasons for each recommendation.
- Score candidates against time, protein, vegetables, carb frequency, effort, preference fit, prior outcomes, ingredient overlap, and current availability confidence.
- Most offered meals must meet the target total time. Exceptions must be labeled.
- Do not repeatedly recommend a failed or paused recipe unless the failure has a documented mitigation.
- Present choices before building a cart unless the user explicitly delegates selection.

### 3. Scaling and consolidation

- Scale every selected recipe from its canonical yield to the run's serving count.
- Preserve units and distinguish count, weight, and volume.
- Round purchasing quantities up to purchasable package sizes, but keep recipe-use quantities separate from purchased quantities.
- Consolidate shared ingredients across recipes before product selection.
- Subtract trusted pantry quantities only when `checked_at` is recent enough for the ingredient's confidence level.

### 4. Product selection

- Prefer the lowest-effort form that still cooks well: pre-diced, trimmed, washed, florets, tenderloins, jarred garlic, or frozen vegetables where quality remains acceptable.
- Prefer Nature's Promise and Food Lion brands. Choose a national brand only when the quality difference is meaningful, and record the reason.
- Choose grass-fed beef when available. If unavailable, ask before substituting conventional beef unless the run explicitly allows it.
- Match the same SKU and package quantity across channels when comparing prices. If exact matching is impossible, normalize totals and state the mismatch.
- Never treat an availability observation as permanent. Timestamp it and include retailer, store, channel, price, package size, and confidence.

### 5. Cart comparison

- Build draft carts only for selected meals.
- Compare merchandise subtotal, promotions, taxes, service fees, pickup fees, delivery fees, bag fees, tip, and estimated final total.
- Report both total order cost and cost per serving.
- Distinguish one-time pantry purchases from ingredients consumed by the meal.
- Never claim two channels are price-equivalent without matching package sizes and quantities.

### 6. Approval and checkout

- Stop before the final purchase action and show the exact cart, substitutions, fulfillment window, address label, fees, tip, and total.
- Require explicit user confirmation for the final order and for any material cart change after approval.
- Never store payment credentials, passwords, authentication codes, or full private addresses in tracked files.
- If authentication, CAPTCHA, or payment requires the user, hand off cleanly and resume after they finish.

### 7. Closeout and learning

- Save the final run record even if no order was placed.
- Update availability with observed facts and timestamps.
- Add outcomes only after cooking or user feedback; do not infer meal success from purchase completion.
- Create an issue for workflow failures, mismatched products, unavailable items, incorrect quantities, fee surprises, or automation problems.
- Propose preference changes from repeated evidence, but do not silently convert a single outcome into a durable preference.
- Append every durable register change to `registers/change-log.yaml`.

## Register ownership and write-back rules

| Register | Write when | Do not write when |
| --- | --- | --- |
| `preferences.yaml` | User states a durable preference or approves a proposed change | A single recipe succeeds or an item is temporarily unavailable |
| `retailers.yaml` | Store/channel facts or selection policy changes | A transient price changes |
| `pantry.yaml` | Quantity is explicitly reported or verified | Quantity is merely assumed |
| `availability.yaml` | A product/price/package is directly observed | A product is only suggested or remembered |
| `substitutions.yaml` | A substitution is approved, rejected, or evaluated | The agent merely considers an alternative |
| `outcomes.yaml` | The meal is cooked or the user supplies feedback | The cart is built but the meal is not evaluated |
| `issues.yaml` | A failure or recurring friction is observed | A normal approval gate is reached |
| `change-log.yaml` | Any durable tracked register changes | Volatile run-file updates only |

## Data integrity

- IDs are lowercase kebab-case and stable after creation.
- Dates and timestamps use ISO 8601.
- Money uses numeric decimal values plus an explicit three-letter currency.
- Unknown values are `null`, never invented.
- Preserve source and observation time for price and availability facts.
- Run `python scripts/validate.py` before committing.
- Never rewrite historical runs to match current preferences; append corrections or superseding records.

## Git discipline

- Keep user-specific secrets and precise addresses out of Git.
- Commit coherent workflow or data changes with a descriptive message.
- Avoid mixing recipe changes, preference changes, and tooling refactors without documenting all three.
- Do not delete historical outcomes or issues merely because they are resolved; update their status and resolution.

