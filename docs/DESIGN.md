# Personal Chef design

- Status: active
- Owner: user
- Last verified: 2026-09-18
- Scope: product behavior and authority model

## Product intent

Personal Chef is a repository-backed agent operated through chat. It should make planning, buying, and cooking food about as easy as receiving a meal kit without hiding prices, making unsafe assumptions, or removing the user's control over purchases.

The repository is the durable memory. Chat is the interface. Retailer websites are transient execution surfaces.

Each new chat is also a durable encounter. Preserve a concise session record in `sessions/` so the repository explains not only what was ordered, but what the request was, which workflow runs it touched, what succeeded, what failed, and what should happen next. Session records summarize evidence; they do not duplicate raw transcripts or private retailer/account data.

## Target experience

A successful run should usually feel like this:

1. The user gives a lightweight request such as "three easy dinners" or "something hearty for the Instant Pot."
2. The agent fills in safe defaults from known preferences and asks only questions that would materially change the result.
3. The agent proposes or selects meals according to the user's delegation level.
4. The agent presents one consolidated shopping review that ends with one direct question about what is already on hand and what other groceries or household items to add.
5. The user's response records pantry exclusions and additional requests and authorizes cart building to begin immediately.
6. The agent consolidates ingredients, chooses convenient products, builds and compares real carts, and reports both recipe cost and whole-order cost in chat.
7. The user approves the exact order in chat.
8. The agent completes checkout, records what happened, produces dependable cooking instructions, and later learns from actual feedback.

## Core design principles

### Low interaction cost

Use confirmed defaults and common sense for reversible, ordinary decisions. Do not repeatedly ask for information already present in the repository. Interrupt the user only for consequential choices, unavailable authority, safety concerns, or ambiguity that materially changes the meal or price.

### Chat-first remote visibility

The desktop browser is an execution surface, not a user-visible source of truth. When the user is interacting primarily from the mobile app or otherwise cannot see the browser, summarize every retailer state needed for a decision in chat: store and channel, product and package choices, cart changes, substitutions, prices, discounts, fees, tip, fulfillment windows, blockers, and approval requests. Do not ask the user to inspect a browser they cannot see. If authentication, CAPTCHA, or payment requires the user, explain the exact protected handoff in chat and have the user complete it on the authorized device; never request or record passwords, payment credentials, or authentication codes in chat or tracked files.

### New-chat menu intent

An open-ended menu request in a new chat is a request to begin a new meal-planning cycle, not a request to report the latest historical run. Create a fresh run, use the current durable preferences and sufficiently fresh pantry evidence, and account for recent outcomes and flavor repetition when constructing a fresh menu. Reuse or summarize an older run only when the user explicitly refers to that run, its order, or its recipes. The new run remains subject to the normal selection, shopping-review, approval, and checkout gates.

### Consequence-based control

Autonomy depends on impact, not on whether a step is technically easy. Drafting menus, selecting comparable package forms, and repairing an ordinary missing ingredient are normally reversible. Placing an order, changing the protein, introducing an allergen, or materially increasing cost requires explicit approval.

### Evidence over memory

Availability, prices, package sizes, pantry quantities, order status, and fulfillment windows require a source and observation time. Unknown values stay unknown. Historical facts remain historical.

### One source for each kind of truth

- Product behavior and authority: this document.
- Operational sequence and decision rules: `docs/WORKFLOW.md`.
- Acceptance criteria and verification: `docs/QUALITY.md`.
- Data ownership and freshness: `docs/REGISTER_REFERENCE.md`.
- User preferences and policies: `registers/`.
- Validated, repeat-eligible recipes: `recipes/`.
- Run-specific facts and decisions: `runs/`.
- Chat-level intent, chronology, linked work, and retrospective: `sessions/`.
- Private account and delivery details: untracked `local/private.yaml`.
- Sanitized itemized receipt facts: the corresponding `runs/*.yaml`; original receipt files containing private fields: ignored `local/receipts/`.

### One canonical state for the active run

The run's top-level `selection` object is the only authoritative statement of which meals are active. Menus, chat summaries, ingredient plans, carts, approvals, and recipe cards are projections of that selection; they cannot silently redefine it.

Every selection mutation increments `selection.revision` and appends a history event. Interpret selection language deterministically:

- `add`, `also`, `both`, and `another` add a meal while retaining the current selection.
- `replace`, `instead`, `swap`, `only`, and explicit removal language replace or remove meals.
- A bare meal choice replaces nothing when one or more meals are already selected; if the requested meal count would be exceeded, ask one concise clarification before changing state.

Any selection change invalidates downstream shopping review, ingredient reconciliation, cart approval, and recipe-card readiness until each is rebuilt against the new revision. Historical projections remain evidence of what occurred but are never treated as current.

### Deterministic gates

Phase changes are predicates over recorded state, not conversational impressions. A run advances only when the next phase's gate is true. Checkout and physical printing are fail-closed actions: missing, stale, or contradictory evidence stops the action and produces a chat-visible explanation.

Before checkout, every active meal ingredient must resolve to exactly one coverage source: a verified pantry quantity, an allocated cart quantity, or an explicitly approved omission/substitution. Before recipe-card generation or printing, the card set must exactly match the requested active meals and each card must be reconciled to the same final ingredient plan. A card for a meal not covered by the order may be produced only when the user explicitly requests it and the missing-ingredient list is shown in chat.

### Progressive disclosure

The root `AGENTS.md` is a short map. Detailed guidance lives in focused documents that an agent reads only when relevant. This preserves attention for the current task and reduces conflicts and stale instructions.

### Checks beat reminders

When a failure can be detected mechanically, encode a validation rule rather than adding another warning sentence. Human or visual judgment remains appropriate for taste, recipe quality, retailer ambiguity, and artifact appearance.

## System model

The core flow is:

`preferences + pantry + outcomes -> menu -> scaled ingredient plan -> product selections -> comparable carts -> approval -> order -> cooking artifact -> outcome`

Each run is the transaction boundary. It snapshots relevant context, records decisions and observed retailer facts, and preserves the exact approved and final order state. Durable registers change only when their evidence threshold is met.

A session is the encounter boundary. One session may contain no run, one run, or multiple related runs. Runs remain authoritative for transaction state; sessions point to runs and registers rather than copying their detailed cart, receipt, pantry, or preference data. This separation makes chat history discoverable without creating competing sources of truth.

The final itemized receipt is durable historical evidence, not transient retailer state. Preserve a sanitized structured copy in the run with product name, SKU when available, package size, unit count, fulfilled quantity or weight, substitutions, refunds, item price, discounts, fees, tax, tip, and charged total. If the original contains an address, contact data, payment details, or other private fields, keep the original only under ignored `local/receipts/` and link it from the run without copying private values into tracked files.

Additional groceries share the checkout transaction but not the recipe economics. Keep their merchandise cost separate when calculating meal cost and cost per serving.

## Authority model

| Action | Default authority |
| --- | --- |
| Read repository records and current retailer state | Agent may proceed; summarize decision-relevant retailer state in chat |
| Apply confirmed preferences and safe defaults | Agent may proceed |
| Select an ordinary equivalent cut or preparation | Agent may proceed within substitution policy |
| Choose a meal | Present choices unless the user delegates selection |
| Change protein, allergens, recipe identity, or materially increase price | Ask first |
| Submit a final order or materially amend an approved cart | Require explicit confirmation in chat |
| Enter authentication, payment, or CAPTCHA information | User handles the protected step outside chat |
| Convert one meal outcome into a durable preference | Propose; do not silently persist |

## Quantity and package design

Track these separately for every ingredient:

- `recipe_quantity`: amount consumed by the selected recipes after scaling.
- `pantry_quantity`: recently verified amount already available.
- `purchase_quantity`: package combination placed in the cart.
- `allocation`: amount assigned to each selected recipe.
- `expected_remainder`: purchased plus pantry quantity minus allocated recipe use.

Keep recipe allocations separate through product selection and checkout. By default, every carted package unit belongs to exactly one recipe, even when two recipes use the same ingredient. Do not pool package counts into a shared cart quantity unless the user explicitly accepts a shared package and its allocation and remainder are unambiguous.

An instruction such as `use entire package` is valid only when the active run proves that the complete purchased package is allocated to that one recipe. Shared ingredients and uncertain package data must show the recipe-use amount instead.

## Recipe library lifecycle

The recipe library is earned, not speculative. A proposed meal may exist in chat or in the active run while it is being selected, purchased, and cooked, but it is not saved under `recipes/` yet.

Save the final cooked form only after the user positively evaluates it. The saved recipe must describe what was actually cooked, including the equipment mode and accepted substitutions that materially define the result. Link it to the validating run and outcome. Recipes that are rejected, abandoned, or never cooked remain outside the saved library; their run history may still explain what happened.

Saved recipes are eligible for future recommendations and should be weighted by later outcome evidence. A future negative result updates the outcome history and may pause the recipe without erasing prior feedback.

## Recipe research provenance

Every new recipe candidate is grounded in at least one complete recipe published on an identifiable recipe website. Culinary knowledge may be used to adapt that inspiration to the user's equipment, effort, nutrition, serving, and flavor requirements, but must not replace source research. Record the recipe title, publisher, direct URL, access time, and a concise adaptation note in the active run. Present the source link with the candidate and clearly label substantial adaptations; do not copy protected recipe prose.

## Skills, design documents, and checks

Skills are optional delivery mechanisms for narrow expertise such as operating a browser, producing a PDF, or interacting with a particular service. They are not the source of truth for Personal Chef's product behavior.

Design documents capture why the system behaves as it does, the boundaries of authority, and the acceptance criteria that survive model or tool changes. Executable validation enforces objective invariants. This split avoids loading broad procedural text into every interaction while retaining specialized skills where they have measurable value.

## Change protocol

For a material workflow change:

1. Update the relevant design or workflow document.
2. Add or revise acceptance criteria in `docs/QUALITY.md`.
3. Update templates, schemas, or checks if the change can be enforced mechanically.
4. Record the durable change in `registers/change-log.yaml`.
5. Record any motivating failure in `registers/issues.yaml` without deleting the history after resolution.

## Current non-goals

- Building a polished standalone application before the chat workflow is reliable.
- Automating protected authentication or storing payment credentials.
- Maintaining a permanent catalog of retailer prices or availability.
- Replacing user judgment about whether a cooked meal was successful.
- Creating a large custom skill that duplicates repository policy.
