# Operations guide

## Starting a run

Copy the current `templates/run.yaml` to `runs/YYYY-MM-DD-short-description.yaml`, create a unique run ID, set `status: draft`, and add the user's request under `request`. Do not copy selection or approval fields from an older run. The version 2 `selection` object is canonical; increment its revision for every actual selection change and bind shopping review, ingredient planning, approval, and recipe cards to that revision.

## Starting and closing a chat session

For each practical new-chat request, copy `templates/session.yaml` to `sessions/YYYY-MM-DD-short-description.yaml`. Create the session before or alongside any workflow run, then set the run's `session_id` and add the run ID to the session. A session may legitimately have no run when the request is maintenance, explanation, or retrospective work.

Update the session only at meaningful milestones. At closeout, summarize the result, add links to issues, changes, outcomes, and artifacts, record lessons and open follow-up, perform a privacy review, and set the session status to `closed`. Do not paste chat transcripts or duplicate itemized transaction data.

An open-ended menu request in a new chat starts a fresh run by default. Do not answer it by replaying the latest historical menu or order; snapshot current preferences and fresh pantry evidence, use recent runs only for outcome and variety context, and construct a new candidate menu before waiting for meal selection.

## Starting a retailer browser

Food Lion ordering must not depend on an already-open retailer tab. Start or reuse Chrome itself, create a fresh task tab pointed at `https://foodlion.com/`, and verify the returned tab is controllable by reading its title, URL, and page state before interacting with the cart.

The browser-created tab uses the user's normal Chrome profile rather than a guaranteed clean or incognito profile. Saved authentication can therefore be reused, but store, cart, fulfillment method, and pickup-window state may also carry over and must be reverified. If protected authentication is required, follow the checkout authority policy rather than attempting to automate the protected dialog.

Assume the user may be operating from the mobile app and unable to see the desktop browser. Do not make browser visibility a prerequisite for user decisions. Report material retailer state and cart mutations in chat, including product and package choices, substitutions, prices, discounts, fees, fulfillment options, windows, blockers, and approval requests. If a protected step requires the user, state what must be completed on the authorized device without asking for passwords, payment credentials, or authentication codes in chat.

## Adding a recipe

Do not save untested recipe candidates. Keep a new proposal in chat or the active run until the user cooks and positively evaluates it. Then copy `templates/recipe.yaml` into `recipes/<recipe-id>.yaml`, record the final cooked ingredients and method, link the validating run and outcome, and run validation.

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

## Printable recipe validation

Use the printable-recipe acceptance criteria in `docs/QUALITY.md`. Keep the validation internal unless a failure needs user input.

## Maintaining project knowledge

Keep `AGENTS.md` short and navigational. Put product decisions in `docs/DESIGN.md`, procedures in `docs/WORKFLOW.md`, acceptance criteria in `docs/QUALITY.md`, and data rules in `docs/REGISTER_REFERENCE.md`.

When behavior changes, update the relevant design document and its acceptance criteria in the same change. Prefer a mechanical check over an additional reminder when the rule can be verified deterministically.
