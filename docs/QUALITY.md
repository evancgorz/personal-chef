# Quality contract

- Status: active
- Last verified: 2026-09-23
- Purpose: observable acceptance criteria for agent outputs

An output is complete only when the relevant criteria below are satisfied. Validation should remain quiet unless it finds a problem that requires user input.

## Handoff and response acceptance

- Every active version 3 run and version 2 session records exactly one handoff owner, next action, awaited event, and update time.
- The handoff owner is `user` only for a material choice, exact purchase confirmation, protected action, or requested cooked feedback.
- A response ends with no more than one requested user action, and that action matches the recorded handoff.
- Short confirmation language authorizes purchase only at `confirm-exact-cart` and only for the unchanged recorded cart snapshot.
- Reversible agent work continues without a redundant confirmation question.
- Material cart or fulfillment changes invalidate earlier approval and create a fresh exact snapshot before confirmation.

## Menu acceptance

- For an open-ended menu request in a new chat, a fresh run exists and the presented candidates are newly constructed for that run; an older run is not treated as the answer unless the user explicitly requested that run or its recipes.
- Hard dietary constraints and equipment limits are satisfied.
- Serving count, schedule, effort, and budget use the active run values or confirmed defaults.
- Each recommendation has a recipe ID and a concise reason.
- Every new candidate includes at least one recipe-website source with title, publisher, direct URL, access time, and an adaptation note.
- The source was reviewed before the candidate was presented; substantial adaptations and uncertain technique changes are disclosed or cross-checked.
- Nutrition-driven additions have a culinary role in the recipe. A kid-friendly or toddler-friendly label is not supported solely by placing an unrelated vegetable on the side; integrated vegetables document moisture, texture, yield, and timing effects.
- Every candidate is presented with estimated per-serving calories, protein, carbohydrates, and fat; estimates are not represented as finalized nutrition facts.
- The candidates offer meaningfully different dominant flavor profiles; recent successful flavors are not repeated by default.
- Candidate scoring uses the dimensions and weights in `docs/WORKFLOW.md`.
- Failed or paused recipes are excluded unless a documented mitigation applies.
- Most meals meet the target total time; exceptions are labeled.
- Every recipe already stored under `recipes/` has a cooked, positive outcome; new ideas remain unsaved proposals until evaluated.
- The canonical selection has a revision, status, complete active-meal list, and append-only change history.
- Selection language was applied deterministically; the complete resulting selected-meal set was echoed in chat.
- Every downstream record used for shopping, approval, or artifacts references the current selection revision.

## Scaling and ingredient-plan acceptance

- Every recipe is scaled from canonical yield to requested servings.
- Count, weight, and volume units remain distinct.
- Each recipe retains separate ingredient and package-allocation lines through product selection and checkout.
- Pantry subtraction uses sufficiently recent evidence.
- Recipe use, purchased quantity, allocation by recipe, and expected remainder remain separate.
- Package rounding never silently changes the recipe-use quantity.
- Before a second package is selected solely for a small shortfall, the run evaluates a one-package recipe adjustment; any adjustment records the original and adjusted quantities, package size, and why the culinary effect is immaterial.
- One-package adjustments are not used for safety-critical, structurally important, medically necessary, or identity-defining quantities.
- Every carted recipe ingredient records SKU, package count, net quantity per package, total purchased quantity, recipe allocation, and expected remainder.
- Package count multiplied by net package quantity is reconciled against the unmet recipe quantity before approval; duplicate units and full-package excess are either corrected or explicitly justified.
- Every cart package unit is allocated to exactly one named recipe or additional-grocery request; the cart SKU count equals the sum of those allocations, with no unallocated units.
- Every ingredient for every active meal has exactly one terminal coverage status; any `unresolved` row blocks approval.
- Reverse reconciliation finds no cart unit unrelated to an active meal or explicit additional-grocery request.

## Shopping-review acceptance

- The user sees the selected recipe, scaled quantities, equipment, timing, and likely shopping needs before cart construction.
- The review ends with one direct question that collects ingredients already on hand and additional grocery requests in one interaction.
- Pantry exclusions and additional items are recorded separately.
- A clear response records the shopping review response, confirms the shopping list, and authorizes cart building without a redundant second confirmation.
- Cart building does not begin until the shopping list is confirmed; if the response is materially ambiguous, the ambiguity is resolved first.
- If pickup or delivery was not already chosen, that preference is asked after the draft cart or comparison is built and before a fulfillment window is selected.
- Additional groceries are excluded from recipe cost and cost per serving while remaining included in the whole-order total.

## Product and cart acceptance

- Every required ingredient is present, intentionally sourced from verified pantry stock, or covered by an approved substitution.
- Products match the desired ingredient form and brand policy; exceptions include a reason.
- Preparation form is evaluated independently for every recipe allocation; consolidation never replaces a requested diced, washed, trimmed, or ready-to-cook form with a higher-effort form.
- Every Food Lion-brand selection includes a time-stamped active-channel check for a suitable Nature's Promise equivalent and records why the fallback was used.
- Confirmed ingredient-form preferences are applied before SKU selection, including microwave-ready 90-second rice by default and ground ginger when fresh root adds no material benefit.
- Comparisons use matching SKUs and quantities when possible and disclose mismatches otherwise.
- Merchandise, promotions, taxes, all fees, tip, total order cost, and cost per serving are shown separately.
- Recipe merchandise and additional groceries have separate subtotals when both are present.
- Fulfillment windows and prices have retailer, channel, store, and observation timestamps.
- Cart mutations are followed by a state re-read to catch unintended additions or omissions.
- All retailer state needed for a user decision is summarized in chat; browser visibility is never assumed.
- The final cart quantity selector and line-item description are read together so a package count cannot be mistaken for ounces, pounds, or another recipe unit.
- Retailer browser startup does not depend on a pre-existing tab: a fresh Chrome task tab can be created, navigated to the retailer, and verified through its title, URL, and readable page state.
- A fresh Chrome task tab is not treated as a clean browser profile; inherited authentication, store, fulfillment, and cart state are independently verified before use.

## Checkout acceptance

- The pre-purchase summary shows the exact cart, substitutions, fulfillment window, address label, fees, tip, and final estimated total in chat.
- Consequential retailer choices and material cart changes are approved through an explicit chat exchange; a browser display alone is not approval evidence.
- The requested pickup or delivery method is independently reverified on the cart, time-selection surface, and final order summary; session carryover is not accepted as evidence.
- Explicit approval exists for the final purchase and any material post-approval change.
- No private address, password, payment data, or authentication code is written to tracked files or responses.
- Protected authentication, CAPTCHA, and payment handoffs are explained in chat without requesting secrets or codes in chat.
- The order record distinguishes placed, amended, cancelled, and merely quoted states.
- Retailer-specific post-order pickup details are completed and verified when the retailer exposes them only after submission, without recording private values.
- The final itemized receipt is captured from retailer order details or an authorized confirmation email and preserved as sanitized structured data in the run.
- Receipt line items retain product, SKU when available, package size, unit count, fulfilled quantity or weight, substitutions, refunds, item charges, and discounts; receipt totals retain merchandise, promotions, fees, tax, tip, and actual charged total.
- The receipt is reconciled against the approved cart, and discrepancies create run feedback or an issue rather than silently changing history.
- Originals containing private fields are stored only under ignored `local/receipts/`; tracked files never copy addresses, contact data, payment details, or authentication data.
- A past-purchases list without authoritative quantities and final charges does not satisfy receipt evidence. Failed retrieval records the retailer and authorized-email attempts and remains open for follow-up.
- The approved cart snapshot and explicit approval both reference the current selection revision; a selection or material cart change invalidates approval.

## Printable recipe acceptance

Before export, build an internal ingredient-use matrix with one row per final ingredient and one column per method step.

- Every required ingredient appears by its specific name in at least one method step.
- Every ingredient mentioned in the method exists in the final ingredient list.
- Each method occurrence includes the recipe-use quantity in parentheses and matches the ingredient list.
- Ingredient preparation requirements needed to execute the method are explicit in both the ingredient list and the relevant step, including cut size for meat and vegetables.
- The first one or two steps complete practical mise en place before active cooking; later steps do not alternate back to cutting, opening, or measuring unless a long unattended cook justifies it.
- The card has at most six actionable steps in an efficient sequence; simultaneous work is used only when practical, and time, temperature, doneness, and food safety remain explicit.
- A new card includes a suitable photo from its original recipe page with a local copy, page URL, direct image URL, credit, and capture time, or records why that photo could not be used. The photo and credit are legible in the rendered card.
- High-temperature sauteing, searing, and grilling use avocado oil by default; olive oil at high heat requires a documented culinary reason or user override.
- Substitutions are expressed as the final ingredient, not as shopping-history commentary.
- `Use entire package` appears only when a single-recipe allocation and matching purchased quantity are verified.
- Cooking mode, time, release behavior, doneness, and food-safety temperatures are internally consistent.
- The PDF is one page when requested and is rendered to an image for full-page inspection.
- The visual inspection finds no overlap, clipping, illegible text, awkward wrapping, or weak hierarchy.
- The exact requested card titles and IDs were stated in chat before generation or printing and match the active selection unless the user explicitly requested an out-of-selection card.
- Each card records the selection and ingredient-plan revisions used to generate it.
- Each card has a structured YAML source under `artifacts/recipe-cards/`; rendering code contains no embedded recipe content.
- Card ingredients and that meal's final ingredient-plan rows reconcile in both directions; any unpurchased or unresolved ingredient is disclosed in chat before output.
- A current card sourced from a saved recipe has exactly the saved ingredient IDs and canonical quantities.
- The rendered PDF embeds the complete YAML source hash, validation confirms that it matches, and revisions use new filenames rather than overwriting historical PDFs.
- Physical printing uses `Fit to page` after PDF visual validation; printer scaling is checked before the PDF is modified in response to a size complaint.
- The post-print chat update names the printed titles, copy count, printer, and scaling mode.

## Closeout and learning acceptance

- The run is saved even when blocked or cancelled.
- An ordered run does not become `completed` without preserved receipt evidence or an explicit unresolved receipt blocker.
- Availability observations include source and time.
- Workflow failures and fee surprises create issue records.
- Outcomes are written only after cooking or explicit user feedback.
- A single outcome does not silently become a durable preference.
- A new recipe enters `recipes/` only after positive cooking feedback and links back to its validating run and outcome.
- When positive feedback does not identify the exact cooked variation, record the outcome against the run candidate with a final-form blocker; do not invent and save a canonical recipe until the missing preparation details are reported.
- Later feedback supersedes earlier rating language without erasing it; the outcome preserves feedback chronology and identifies the current authoritative assessment.
- A post-cooking recipe revision marks every older recipe-card artifact as superseded for future use while retaining it as historical evidence.
- Every practical new-chat request has one session record, including maintenance and retrospective requests that create no meal run.
- The session links rather than duplicates authoritative run and register facts, contains a concise result and lessons, identifies open follow-up, and contains no raw transcript or private fields.
- Every version 2 run links to exactly one existing session, and that session links back to the run.
- A closed session records `privacy_reviewed: true`.

## Verification layers

| Layer | Method |
| --- | --- |
| Repository structure and cross-references | `python scripts/validate.py` |
| Quantities, cart contents, fees, and order state | Reconcile against the active run and observed retailer surface |
| Recipe completeness | Ingredient-use matrix and bidirectional ingredient/method comparison |
| Printable layout | Render the PDF and inspect the entire image |
| Taste and usefulness | User feedback recorded after cooking |

When a check fails, fix the underlying data or design. Do not weaken the acceptance criterion merely to make validation pass.
