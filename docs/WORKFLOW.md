# End-to-end workflow

## State model

Each run moves through these states:

`draft -> menu-presented -> meals-selected -> cart-building -> comparison-ready -> awaiting-approval -> ordered -> completed`

Alternative terminal states are `cancelled` and `blocked`. A blocked run records the blocker and the next action required.

## Menu scoring

Use a 100-point score to keep recommendations consistent:

| Dimension | Weight | Guidance |
| --- | ---: | --- |
| Preference and dietary fit | 25 | Hard constraints first; durable preferences second |
| Protein quality and amount | 20 | Favor meals meeting the configured target |
| Vegetable quantity and variety | 15 | Favor substantial, varied vegetables |
| Total time | 15 | Full points at or below the target |
| Preparation effort | 10 | Reward ready-to-cook ingredients and simple cleanup |
| Prior outcome | 5 | Reward proven meals without making the menu repetitive |
| Ingredient overlap and waste | 5 | Reward useful overlap across selected meals |
| Availability confidence | 5 | Reward recently observed, in-stock products |

Hard allergy and exclusion rules are filters, not scoring dimensions.

## Quantity logic

For each ingredient, retain three values:

- `required_quantity`: what the scaled recipe consumes.
- `purchase_quantity`: the smallest package combination that covers the requirement.
- `expected_remainder`: purchase quantity minus required quantity.

When comparing channels, normalize by usable quantity. A cheaper cart with substantially more or less food is not an equal comparison.

## Price comparison

Every channel estimate should record:

- item subtotal;
- promotions and loyalty discounts;
- taxes;
- service, pickup, delivery, priority, and bag fees;
- tip, including the assumed rate or amount;
- estimated out-the-door total;
- cost per serving;
- timestamp and fulfillment window;
- SKU mismatches or weight uncertainty.

Weighted products must include the requested weight, displayed unit price, and estimated extended price.

## Learning loop

After a meal, ask only for information that improves future decisions: overall rating, effort accuracy, time accuracy, portion adequacy, leftovers, ingredient quality, substitutions, and whether to repeat. Use repeated evidence to propose preference changes. Record isolated feedback as an outcome.

