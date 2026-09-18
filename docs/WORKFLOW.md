# End-to-end workflow

- Status: active
- Last verified: 2026-09-18
- Governing design: `docs/DESIGN.md`
- Acceptance criteria: `docs/QUALITY.md`

## State model

Each run moves through these states:

`draft -> menu-presented -> meals-selected -> review-ready -> shopping-list-confirmed -> cart-building -> comparison-ready -> awaiting-approval -> ordered -> completed`

Alternative terminal states are `cancelled` and `blocked`. A blocked run records the blocker and the next action required. Record every phase transition in the run file.

The following gates are authoritative. Do not advance because the conversation merely appears ready:

| Transition | Required recorded predicate |
| --- | --- |
| `menu-presented -> meals-selected` | `selection.status: confirmed`, at least one active meal ID, and the count matches the request or a recorded override |
| `meals-selected -> review-ready` | Every active meal has a final scaled plan and disclosed source adaptations |
| `review-ready -> shopping-list-confirmed` | Shopping-review response recorded for the current selection revision, with pantry exclusions and additional items separated |
| `shopping-list-confirmed -> cart-building` | `cart_build_authorized: true` for that same revision |
| `cart-building -> comparison-ready` | Ingredient-to-cart reconciliation passes with no unresolved active-meal ingredient |
| `comparison-ready -> awaiting-approval` | Exact chat-visible cart snapshot exists and references the current selection revision |
| `awaiting-approval -> ordered` | Explicit approval references the unchanged cart snapshot and current selection revision |
| `ordered -> completed` | Receipt requirement in section 9 is satisfied |

If a predicate becomes false, move back to the earliest affected phase and mark downstream projections stale. Never repair a contradiction by silently changing the active selection.

## 1. Intake

At the start of each practical new-chat request, create one session record from `templates/session.yaml`. Record a short user-intent summary and link any run created for the request. If the request is informational or maintenance-only, keep the session even when no meal-to-order run is needed. Never copy the raw transcript, credentials, addresses, payment information, authentication codes, or other private fields into the session.

Resolve meal count, serving count, schedule, budget, allergies, dislikes, equipment limits, and fulfillment preference. Use durable preferences when the user does not override them.

A run-specific instruction affects only that run unless the user states or confirms that it should persist. Ask only when missing information would materially alter the result or authorization is required.

When an open-ended menu request arrives in a new chat, treat it as a new meal-planning cycle by default. Create a fresh run rather than summarizing or resuming an older run. Use the configured defaults for omitted details, carry forward only current durable preferences and sufficiently fresh pantry evidence, and use recent runs for variety and outcome context rather than as the active menu. If a missing detail would materially change the menu, ask one concise question; otherwise proceed to a fresh menu. Fulfillment preference may remain unresolved until after the draft cart or comparison is visible; do not insert that question between the shopping review and cart construction. Do not build a cart until the user selects meals and responds to the consolidated shopping review.

## 2. Menu construction

Build a varied menu with stable recipe IDs and concise reasons. Present choices before building a cart unless the user explicitly delegates selection.

Rotate dominant flavor families across recommendations and recent runs. A positive outcome is evidence that a recipe may be repeated, not permission to make its signature ingredient the default for other recipes. When several candidates are presented together, avoid giving them the same dominant flavor unless the user requested it.

Before presenting any new candidate, inspect at least one complete recipe on an identifiable recipe website. Store its title, publisher, direct URL, access time, and the planned adaptation in the active run, and include the source link in the recommendation. Prefer tested editorial sources or established recipe developers. Cross-check a second source when making a substantial technique change or when doneness, food safety, or equipment conversion is uncertain. Do not present an invented concept first and search for a source afterward.

Treat nutrition-driven additions as recipe adaptations, not box-checking sides. For a meal described as kid-friendly or toddler-friendly, integrate a mild vegetable into a familiar component when the source and cooking method can support it—for example, finely grated vegetables cooked into a sauce—unless the user requested a separate side. Record how moisture, texture, yield, and cooking time are adjusted. Never add an unrelated vegetable side merely to improve the candidate's score, and disclose when the adaptation is substantial.

Present each candidate like a concise restaurant-menu entry: the dish title links to its recipe inspiration, followed by an appetizing one-line description and small bullets for estimated calories, protein, carbohydrates, and fat per serving. Clearly label planning-stage macros as estimates. Recalculate them from the final scaled ingredient plan after selection.

Saved recipes in `recipes/` are already user-validated and may be recommended again. New recipe ideas remain proposals in chat or the active run; do not add them to `recipes/` before cooking feedback.

Maintain the top-level canonical selection after every user choice. Echo the complete current set in chat, for example, `Selected meals (2): A; B.` Apply the deterministic add/replace language rules from `docs/DESIGN.md`. When intent is still ambiguous and would change which meals are purchased, ask before mutating the selection. Increment the revision on every actual change and invalidate all downstream records tied to an older revision.

Use this 100-point score:

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

Hard allergy and exclusion rules are filters, not scoring dimensions. Do not repeatedly recommend a failed or paused recipe unless its failure has a documented mitigation. Label total-time exceptions.

## 3. Shopping review

After meal selection and before opening a retailer cart, present one concise review containing:

- selected recipes, servings, equipment, timing, and a short method summary;
- scaled recipe-use quantities;
- the expected items to purchase, with pantry candidates clearly separated;
- a single direct question asking which listed ingredients are already on hand and what unrelated groceries or household items should be added.

Wait for the user's response before cart construction. Treat pantry statements as run-specific evidence unless the user supplies a durable quantity or asks to update pantry inventory. On response, record pantry exclusions and additional groceries separately, mark the shopping list confirmed, and proceed directly to cart construction. Do not ask a second shopping-list confirmation when the response is clear; pause only if it materially changes the selected meal, introduces a protected substitution decision, or leaves the required quantities ambiguous. Additional groceries remain included in the order total but excluded from recipe cost and cost per serving.

## 4. Scaling, consolidation, and allocation

Scale every selected recipe from canonical yield to the run's serving count. Preserve units and distinguish counts, weights, and volumes.

For each ingredient, retain:

- `recipe_quantity`: the amount the scaled recipes consume.
- `pantry_quantity`: the sufficiently recent verified amount on hand.
- `purchase_quantity`: the smallest package combination covering the unmet requirement.
- `allocation`: the amount assigned to each selected recipe.
- `expected_remainder`: purchased plus pantry quantity minus allocated use.

Keep each recipe's ingredient lines separate through product selection and cart review. Assign every purchased package unit to one recipe before adding it to the cart. Combine a package across recipes only when the user explicitly accepts that shared purchase and the allocation and expected remainder are recorded unambiguously. Round each recipe's purchases up to real package sizes without changing recipe-use quantities. Subtract pantry stock only when its `checked_at` evidence meets the freshness rules in `docs/REGISTER_REFERENCE.md`.

Before cart approval, reconcile each recipe ingredient against the actual cart line: recipe ID, SKU, unit count, net quantity per unit, total purchased quantity, recipe allocation, and expected remainder. Treat the retailer quantity selector as a package count, not an ingredient amount. The cart's SKU quantity must equal the sum of package units allocated to named recipes or additional groceries. Investigate any unallocated unit, line with more than one unit, or expected remainder of at least one full package; disclose intentional bulk purchases and correct accidental duplicates before presenting the cart.

Write one reconciliation row for every ingredient in every active meal, including pantry-only ingredients. Each row must end in exactly one status: `covered-by-pantry`, `covered-by-cart`, `approved-substitution`, or `approved-omission`. `unresolved` blocks cart approval. Also perform the reverse check: every cart unit must map to an active meal or an additional-grocery request. Store the selection revision used by the reconciliation.

## 5. Product selection

Prefer the lowest-effort form that still cooks well: pre-diced, trimmed, washed, florets, tenderloins, jarred garlic, or frozen vegetables where quality remains acceptable. Apply this separately to every recipe allocation. If one recipe needs onion wedges while another needs diced onion, buy the suitable form for each recipe; do not create chopping work merely to consolidate the purchase.

Apply confirmed ingredient-form defaults before product search. Default to microwave-ready 90-second rice when a suitable variety is available because it minimizes preparation and cleanup; use dry rice with Instant Pot directions only when the user requests it or no suitable pouch is available. Prefer ground ginger when it preserves the recipe's role, and select fresh ginger root only when its fresh aroma or texture is material. Recalculate recipe quantities whenever the ingredient form changes rather than treating fresh and ground forms as equal measures.

Use Nature's Promise first, then Food Lion. Before selecting a Food Lion product, search for a suitable Nature's Promise equivalent in the active store and fulfillment channel and record the availability result; absence of a recorded check is not evidence that Nature's Promise was unavailable. Choose a national brand only when the quality difference is meaningful and record the reason. Choose grass-fed beef when available; ask before substituting conventional beef unless the run explicitly allows it.

For ordinary ingredient gaps, search in this order:

1. The same ingredient in an equivalent convenient cut or preparation.
2. The same ingredient in a standard fresh or frozen form.
3. The closest functional culinary equivalent that preserves the recipe.

Ask before allergens, a different protein, a material recipe change, or a material price increase.

Every availability observation records retailer, store, channel, price, package size, observation time, and confidence. Availability is never permanent.

## 6. Cart construction and comparison

Build draft carts only for selected meals. Scope every cart action to the named product and re-read cart state after each mutation.

Treat the retailer browser as invisible to the user when the user is working from the mobile app. Use chat as the user-visible record: after each material cart mutation, summarize what was added, removed, substituted, or still unavailable, and report the store, channel, package count, item price, discounts, fees, fulfillment options, and any decision the user must make. Do not ask the user to inspect or verify a browser surface they cannot see.

For Food Lion, use Chrome by default and do not require a Food Lion tab to be open already. If no suitable task tab exists, create a fresh Chrome task tab, navigate it to `https://foodlion.com/`, and verify control by re-reading its title, URL, and page state before cart work. A fresh task tab still shares the user's normal Chrome profile and may inherit authentication, store, pickup, delivery, or cart context; treat all inherited retailer state as untrusted carryover. Verify pickup versus delivery before product review, after any store or method change, when selecting a window, and again on the final order summary. A method change may clear the selected window, so reselect and re-read it before checkout.

Match the same SKU and package quantity across channels when comparing. When exact matching is impossible, normalize totals and describe the mismatch.

If the user did not already choose pickup or delivery, ask for that preference after the draft cart or pickup-versus-delivery comparison is built and before selecting a fulfillment window. If the active preference is `compare`, show the relevant options and ask which method to use. This fulfillment question must not delay cart construction after a clear shopping-review response.

Report:

- merchandise subtotal;
- promotions and loyalty discounts;
- taxes;
- service, pickup, delivery, priority, bag, and other fees;
- tip and its assumption;
- estimated out-the-door total;
- cost per serving;
- fulfillment window and observation time;
- weighted-item assumptions and package mismatches;
- one-time pantry purchases separately from meal consumption.
- additional non-recipe groceries separately from meal merchandise and cost per serving.

## 7. Approval and checkout

Before the final purchase action, present the exact cart, substitutions, fulfillment window, address label, fees, tip, and total in chat. Require explicit user confirmation in chat; the browser's displayed state is not a substitute for a chat-visible approval request.

Require new confirmation in chat for a material cart change after approval. If authentication, CAPTCHA, or payment entry requires the user, explain the protected handoff and the required action in chat, then resume after completion. Never ask the user to send protected credentials or codes in chat, and never store or expose them.

After submission, verify the retailer's actual order state and record the confirmation reference, final window, totals, and amendments. Do not confuse a quote, saved cart, or selected slot with a placed order.

Immediately after checkout, capture the retailer's final itemized receipt or order detail. If the retailer surface does not expose it, search the user's authorized email account for the retailer confirmation. Preserve the original under ignored `local/receipts/` when it contains private fields, and write a sanitized structured receipt into the run. Reconcile the receipt against the approved cart and record fulfilled quantities, weighted-item adjustments, substitutions, omissions, refunds, promotions, fees, tax, tip, and the actual charged total. A past-purchases product list without final quantities and charges is not a receipt. If no authoritative receipt is obtainable, record the sources checked, timestamps, and blocker; leave receipt follow-up open rather than reconstructing it from memory.

Food Lion may request pickup-identification details only after the order is submitted. Complete the post-order pickup-preferences prompt from the user's current instruction or untracked private configuration, then verify that the preference was accepted. Never copy the phone number or other private values into tracked records.

## 8. Cooking artifact

Generate cooking instructions from the final scaled ingredient plan, not from the original canonical recipe or shopping history. Express substitutions as the final ingredient names.

Front-load mise en place into the first one or two steps: cut proteins and vegetables, open cans, and measure ingredients before heat begins. After cooking starts, do not send the cook back to preparation tasks unless a genuinely long unattended cooking interval makes that sequencing easier. Use avocado oil for high-temperature sauteing, searing, and grilling; reserve olive oil for lower-temperature or uncooked flavor uses when appropriate.

Run the printable-recipe acceptance checks in `docs/QUALITY.md`, including ingredient-to-method reconciliation, quantity consistency, cautious full-package labels, and full-page visual inspection.

Before generating or printing, state the exact card titles in chat and compare their IDs with the requested card set. By default that set is the canonical active selection. A stale card, an old output-directory file, or a previously selected meal is never an implicit print target. Record the selection revision and ingredient-plan revision used for each card.

Perform a bidirectional coverage check before export: every card ingredient must appear in the final ingredient plan, and every planned ingredient for that meal must appear on the card or be explicitly identified as non-recipe. If the meal was not shopped, show its missing ingredients in chat before generating or printing it.

For physical printing, first verify that the PDF itself passes full-page visual inspection, then use printer scaling `Fit to page`. A print-size complaint does not authorize regenerating or rescaling the PDF until printer scaling has been checked. After printing, report the exact titles, copy count, printer, and scaling mode in chat.

## 9. Closeout and learning

Save the final run record even if no order was placed. An ordered run is not `completed` until an authoritative itemized receipt has been preserved and reconciled, or the run explicitly records why retrieval remains blocked. Update availability with observed facts and timestamps. Create an issue for workflow failures, mismatched products, unavailable items, incorrect quantities, fee surprises, or automation problems.

After cooking, ask only for feedback that improves future decisions: overall rating, effort accuracy, time accuracy, portion adequacy, leftovers, ingredient quality, substitutions, and whether to repeat. Add outcomes only from cooking or user feedback. Propose durable preference changes from repeated evidence rather than silently promoting a single result.

When the user positively evaluates a new recipe, save the final cooked version under `recipes/`, mark it `validated`, and link it to the run and outcome. Do not retain untested candidate recipe files.

Close the session separately from the run. Summarize the delivered result, link all affected run, issue, change, outcome, and artifact IDs or paths, record concise lessons and unresolved follow-up, and set `privacy_reviewed: true`. A chat ending does not imply that an ordered run is complete; preserve its receipt or cooking follow-up independently.
