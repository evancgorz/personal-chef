from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import yaml
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_RUN_STATES = {
    "draft",
    "menu-presented",
    "meals-selected",
    "review-ready",
    "shopping-list-confirmed",
    "cart-building",
    "comparison-ready",
    "awaiting-approval",
    "ordered",
    "completed",
    "cancelled",
    "blocked",
}
ORDERED_RUN_STATES = [
    "draft",
    "menu-presented",
    "meals-selected",
    "review-ready",
    "shopping-list-confirmed",
    "cart-building",
    "comparison-ready",
    "awaiting-approval",
    "ordered",
    "completed",
]
TERMINAL_COVERAGE = {"covered-by-pantry", "covered-by-cart", "approved-substitution", "approved-omission"}
HANDOFF_OWNERS = {"agent", "user", "external", "none"}


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_handoff(data: dict, record_name: str, errors: list[str]) -> None:
    handoff = data.get("handoff") or {}
    owner = handoff.get("owner")
    next_action = handoff.get("next_action")
    require(owner in HANDOFF_OWNERS, f"{record_name} has invalid handoff owner", errors)
    require(isinstance(next_action, str) and bool(next_action), f"{record_name} lacks handoff next_action", errors)
    require(isinstance(handoff.get("waiting_for"), str) and bool(handoff.get("waiting_for")), f"{record_name} lacks handoff waiting_for", errors)
    require(bool(handoff.get("updated_at")), f"{record_name} lacks handoff updated_at", errors)
    if owner == "none":
        require(next_action == "none", f"{record_name} with no handoff owner must use next_action none", errors)


def validate() -> list[str]:
    errors: list[str] = []
    required = [
        ROOT / "AGENTS.md",
        ROOT / "docs/DESIGN.md",
        ROOT / "docs/WORKFLOW.md",
        ROOT / "docs/QUALITY.md",
        ROOT / "docs/REGISTER_REFERENCE.md",
        ROOT / "docs/OPERATIONS.md",
        ROOT / "templates/session.yaml",
        ROOT / "registers/preferences.yaml",
        ROOT / "registers/retailers.yaml",
        ROOT / "registers/pantry.yaml",
        ROOT / "registers/availability.yaml",
        ROOT / "registers/substitutions.yaml",
        ROOT / "registers/outcomes.yaml",
        ROOT / "registers/issues.yaml",
        ROOT / "registers/change-log.yaml",
    ]
    for path in required:
        require(path.exists(), f"missing required file: {path.relative_to(ROOT)}", errors)

    agents_path = ROOT / "AGENTS.md"
    if agents_path.exists():
        agents_text = agents_path.read_text(encoding="utf-8")
        require(len(agents_text.splitlines()) <= 100, "AGENTS.md must remain a compact map of 100 lines or fewer", errors)
        for document in ("docs/DESIGN.md", "docs/WORKFLOW.md", "docs/QUALITY.md", "docs/REGISTER_REFERENCE.md"):
            require(document in agents_text, f"AGENTS.md must link to {document}", errors)

    for document in ("DESIGN.md", "WORKFLOW.md", "QUALITY.md"):
        path = ROOT / "docs" / document
        if path.exists():
            text = path.read_text(encoding="utf-8")
            require("Status: active" in text, f"docs/{document} must declare active status", errors)
            require("Last verified:" in text, f"docs/{document} must declare a verification date", errors)

    yaml_paths = sorted(
        p
        for directory in ("registers", "recipes", "runs", "sessions", "templates")
        for p in (ROOT / directory).glob("*.yaml")
    )
    documents = {}
    for path in yaml_paths:
        try:
            documents[path] = load_yaml(path)
        except Exception as exc:
            errors.append(f"invalid YAML in {path.relative_to(ROOT)}: {exc}")

    recipe_ids: set[str] = set()
    recipe_documents: dict[str, dict] = {}
    for path in sorted((ROOT / "recipes").glob("*.yaml")):
        data = documents.get(path) or {}
        recipe_id = data.get("id")
        require(isinstance(recipe_id, str) and bool(KEBAB.fullmatch(recipe_id)), f"invalid recipe id in {path.name}", errors)
        if isinstance(recipe_id, str):
            require(recipe_id not in recipe_ids, f"duplicate recipe id: {recipe_id}", errors)
            recipe_ids.add(recipe_id)
            recipe_documents[recipe_id] = data
        require(data.get("status") == "validated", f"saved recipe must be validated: {path.name}", errors)
        require(data.get("canonical_yield", 0) > 0, f"canonical_yield must be positive in {path.name}", errors)
        total = (data.get("time") or {}).get("total_minutes")
        require(isinstance(total, (int, float)) and total > 0, f"total_minutes must be positive in {path.name}", errors)
        require(bool(data.get("ingredients")), f"recipe has no ingredients: {path.name}", errors)
        require(bool(data.get("instructions")), f"recipe has no instructions: {path.name}", errors)

    card_ids: set[str] = set()
    card_outputs: set[str] = set()
    for path in sorted((ROOT / "artifacts" / "recipe-cards").glob("**/*.yaml")):
        try:
            card = load_yaml(path) or {}
        except Exception as exc:
            errors.append(f"invalid recipe-card YAML in {path.relative_to(ROOT)}: {exc}")
            continue
        card_id = card.get("id")
        output_filename = card.get("output_filename")
        require(card.get("version") == 1, f"unsupported recipe-card version in {path.relative_to(ROOT)}", errors)
        require(isinstance(card_id, str) and bool(KEBAB.fullmatch(card_id)), f"invalid recipe-card id in {path.relative_to(ROOT)}", errors)
        require(card_id not in card_ids, f"duplicate recipe-card id: {card_id}", errors)
        card_ids.add(card_id)
        require(isinstance(output_filename, str) and output_filename.endswith(".pdf"), f"invalid recipe-card output in {path.relative_to(ROOT)}", errors)
        require(output_filename not in card_outputs, f"duplicate recipe-card output: {output_filename}", errors)
        card_outputs.add(output_filename)
        for field in ("status", "source", "reconciliation", "title", "meta", "deck", "equipment", "ingredients", "steps", "tip"):
            require(bool(card.get(field)), f"recipe-card {card_id} lacks {field}", errors)
        steps = card.get("steps") or []
        if card.get("card_format") == 2:
            require(isinstance(steps, list) and 1 <= len(steps) <= 6, f"recipe-card {card_id} must have 1 to 6 steps", errors)
            require(bool(card.get("source_photo") or card.get("source_photo_unavailable_reason")), f"recipe-card {card_id} needs a source photo or an unavailable reason", errors)
        photo = card.get("source_photo")
        if photo:
            for field in ("path", "page_url", "image_url", "credit", "captured_at"):
                require(bool(photo.get(field)), f"recipe-card {card_id} source photo lacks {field}", errors)
            photo_path_text = photo.get("path")
            if isinstance(photo_path_text, str):
                photo_path = (ROOT / photo_path_text).resolve()
                require(photo_path.is_relative_to(ROOT) and photo_path.is_file(), f"recipe-card {card_id} source photo does not exist in repository", errors)
        elif card.get("source_photo_unavailable_reason"):
            require(isinstance(card["source_photo_unavailable_reason"], str), f"recipe-card {card_id} has invalid photo reason", errors)
        for section in card.get("ingredients") or []:
            require(bool(section.get("section")), f"recipe-card {card_id} has untitled ingredient section", errors)
            require(bool(section.get("items")), f"recipe-card {card_id} has empty ingredient section", errors)
            for item in section.get("items") or []:
                require(bool(item.get("display")), f"recipe-card {card_id} has ingredient without display text", errors)

        source = card.get("source") or {}
        source_path_text = source.get("path")
        if source_path_text:
            source_path = (ROOT / source_path_text).resolve()
            require(source_path.is_relative_to(ROOT), f"recipe-card {card_id} source escapes repository", errors)
            require(source_path.exists(), f"recipe-card {card_id} source does not exist: {source_path_text}", errors)
        if source.get("kind") == "saved-recipe":
            recipe_id = source.get("recipe_id")
            recipe = recipe_documents.get(recipe_id) or {}
            require(bool(recipe), f"recipe-card {card_id} references unknown saved recipe {recipe_id}", errors)
            canonical = {item.get("id"): item for item in recipe.get("ingredients") or []}
            represented: set[str] = set()
            for section in card.get("ingredients") or []:
                for item in section.get("items") or []:
                    ingredient_id = item.get("source_ingredient_id")
                    represented.add(ingredient_id)
                    require(ingredient_id in canonical, f"recipe-card {card_id} references unknown ingredient {ingredient_id}", errors)
                    if ingredient_id in canonical:
                        expected = {"quantity": canonical[ingredient_id].get("quantity"), "unit": canonical[ingredient_id].get("unit")}
                        require(item.get("source_quantity") == expected, f"recipe-card {card_id} quantity drift for {ingredient_id}", errors)
            require(represented == set(canonical), f"recipe-card {card_id} ingredient set differs from saved recipe {recipe_id}", errors)
        if card.get("status") == "current" and isinstance(output_filename, str):
            require((card.get("reconciliation") or {}).get("status") == "reconciled", f"current recipe-card {card_id} is not reconciled", errors)
            output_path = ROOT / "output" / "pdf" / output_filename
            require(output_path.exists(), f"current recipe-card {card_id} lacks rendered PDF {output_filename}", errors)
            if output_path.exists():
                source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                try:
                    metadata = PdfReader(output_path).metadata or {}
                    require(metadata.get("/Subject") == f"Source SHA256: {source_hash}", f"recipe-card PDF {output_filename} was not rendered from its current YAML source", errors)
                    require(len(PdfReader(output_path).pages) == 1, f"recipe-card PDF {output_filename} is not one page", errors)
                except Exception as exc:
                    errors.append(f"cannot inspect recipe-card PDF {output_filename}: {exc}")

    renderer_path = ROOT / "scripts" / "build_recipe_cards.py"
    if renderer_path.exists():
        renderer_text = renderer_path.read_text(encoding="utf-8")
        require("CARDS =" not in renderer_text, "recipe-card renderer must not contain hard-coded card data", errors)
        require("artifacts" in renderer_text and "recipe-cards" in renderer_text, "recipe-card renderer must load structured card sources", errors)

    retailer_data = documents.get(ROOT / "registers/retailers.yaml") or {}
    retailer_ids = {item.get("id") for item in retailer_data.get("retailers", []) if item.get("id")}
    for retailer_id in retailer_ids:
        require(bool(KEBAB.fullmatch(retailer_id)), f"invalid retailer id: {retailer_id}", errors)

    session_documents: dict[str, dict] = {}
    for path in sorted((ROOT / "sessions").glob("*.yaml")):
        data = documents.get(path) or {}
        session_id = data.get("id")
        require(isinstance(session_id, str) and bool(KEBAB.fullmatch(session_id)), f"invalid session id in {path.name}", errors)
        if isinstance(session_id, str):
            require(session_id not in session_documents, f"duplicate session id: {session_id}", errors)
            session_documents[session_id] = data
        require(data.get("status") in {"active", "closed"}, f"invalid session status in {path.name}", errors)
        require(bool(data.get("request_summary")), f"session lacks request summary in {path.name}", errors)
        if data.get("version", 1) >= 2:
            validate_handoff(data, f"session {session_id}", errors)
        if data.get("status") == "closed":
            require(bool(data.get("closed_at")), f"closed session lacks closed_at in {path.name}", errors)
            require(bool(data.get("result_summary")), f"closed session lacks result summary in {path.name}", errors)
            require(data.get("privacy_reviewed") is True, f"closed session lacks privacy review in {path.name}", errors)

    run_ids: set[str] = set()
    for path in sorted((ROOT / "runs").glob("*.yaml")):
        data = documents.get(path) or {}
        run_id = data.get("id")
        require(isinstance(run_id, str) and bool(KEBAB.fullmatch(run_id)), f"invalid run id in {path.name}", errors)
        if isinstance(run_id, str):
            require(run_id not in run_ids, f"duplicate run id: {run_id}", errors)
            run_ids.add(run_id)
        require(data.get("status") in VALID_RUN_STATES, f"invalid run status in {path.name}", errors)
        if data.get("version", 1) >= 3:
            validate_handoff(data, f"run {run_id}", errors)
            if data.get("status") == "awaiting-approval":
                handoff = data.get("handoff") or {}
                require(handoff.get("owner") == "user" and handoff.get("next_action") == "confirm-exact-cart", f"awaiting-approval run {run_id} must wait for exact-cart confirmation", errors)
        if data.get("version", 1) >= 2:
            require(data.get("session_id") in session_documents, f"version 2 run lacks a valid session link in {path.name}", errors)
            selection = data.get("selection") or {}
            revision = selection.get("revision")
            active_meal_ids = selection.get("active_meal_ids") or []
            require(isinstance(revision, int) and revision >= 0, f"version 2 run has invalid selection revision in {path.name}", errors)
            require(selection.get("status") in {"pending", "confirmed"}, f"version 2 run has invalid selection status in {path.name}", errors)
            require(len(active_meal_ids) == len(set(active_meal_ids)), f"version 2 run has duplicate active meals in {path.name}", errors)
            require(isinstance(selection.get("history"), list), f"version 2 run lacks selection history in {path.name}", errors)
            candidates = ((data.get("menu") or {}).get("candidate_recipe_ids") or [])
            for meal_id in active_meal_ids:
                require(meal_id in candidates, f"active meal {meal_id} is not a candidate in {path.name}", errors)

            status = data.get("status")
            phase_index = ORDERED_RUN_STATES.index(status) if status in ORDERED_RUN_STATES else -1
            if phase_index >= ORDERED_RUN_STATES.index("meals-selected"):
                require(selection.get("status") == "confirmed" and bool(active_meal_ids), f"advanced run lacks confirmed active meals in {path.name}", errors)
            if phase_index >= ORDERED_RUN_STATES.index("shopping-list-confirmed"):
                review = data.get("shopping_review") or {}
                require(review.get("selection_revision") == revision, f"shopping review is stale in {path.name}", errors)
                require(review.get("cart_build_authorized") is True, f"shopping review does not authorize cart building in {path.name}", errors)
            if phase_index >= ORDERED_RUN_STATES.index("comparison-ready"):
                require(data.get("ingredient_plan_selection_revision") == revision, f"ingredient plan is stale in {path.name}", errors)
                plan = data.get("ingredient_plan") or []
                require(bool(plan), f"comparison-ready run lacks ingredient plan in {path.name}", errors)
                for item in plan:
                    require(item.get("coverage_status") in TERMINAL_COVERAGE, f"ingredient {item.get('ingredient', 'unknown')} is unresolved in {path.name}", errors)
                active_plan_meals = {item.get("recipe_id") for item in plan}
                for meal_id in active_meal_ids:
                    require(meal_id in active_plan_meals, f"active meal {meal_id} has no ingredient coverage in {path.name}", errors)
            if phase_index >= ORDERED_RUN_STATES.index("awaiting-approval"):
                approval = data.get("approval") or {}
                require(approval.get("selection_revision") == revision, f"approval is stale in {path.name}", errors)
                require(bool(approval.get("cart_snapshot_id")), f"approval lacks cart snapshot in {path.name}", errors)

            for card in ((data.get("artifacts") or {}).get("recipe_cards") or []):
                card_name = card.get("title") or card.get("meal_id") or "unknown"
                for field in ("meal_id", "title", "selection_revision", "ingredient_plan_revision", "coverage_status"):
                    require(field in card, f"recipe card {card_name} lacks {field} in {path.name}", errors)
                require(card.get("selection_revision") == revision, f"recipe card {card_name} is stale in {path.name}", errors)
                require(card.get("coverage_status") in {"reconciled", "missing-items-disclosed"}, f"recipe card {card_name} lacks coverage disposition in {path.name}", errors)
                if card.get("printed_at"):
                    require(card.get("scaling_mode") == "fit-to-page", f"printed recipe card {card_name} did not use fit-to-page in {path.name}", errors)
        selected = ((data.get("menu") or {}).get("selected_recipe_ids") or [])
        for recipe_id in selected:
            require(recipe_id in recipe_ids, f"unknown recipe {recipe_id} in {path.name}", errors)
        menu = data.get("menu") or {}
        candidates = menu.get("candidate_recipe_ids") or []
        created_at = str(data.get("created_at") or "")
        provenance_required = created_at >= "2026-09-10T08:10:20-04:00" or path.name == "run-2026-09-10-grill-meal.yaml"
        if candidates and data.get("status") != "draft" and provenance_required:
            sources = menu.get("sources") or []
            sourced_ids = {source.get("recipe_id") for source in sources}
            for recipe_id in candidates:
                require(recipe_id in sourced_ids, f"candidate {recipe_id} lacks recipe-website provenance in {path.name}", errors)
            for source in sources:
                source_id = source.get("recipe_id") or "unknown"
                require(bool(source.get("title")), f"source {source_id} lacks title in {path.name}", errors)
                require(bool(source.get("publisher")), f"source {source_id} lacks publisher in {path.name}", errors)
                require(str(source.get("url", "")).startswith(("https://", "http://")), f"source {source_id} lacks direct URL in {path.name}", errors)
                require(bool(source.get("accessed_at")), f"source {source_id} lacks access time in {path.name}", errors)
                require(bool(source.get("adaptation")), f"source {source_id} lacks adaptation note in {path.name}", errors)
            macros = menu.get("macro_estimates") or []
            macro_by_id = {item.get("recipe_id"): item for item in macros}
            for recipe_id in candidates:
                estimate = macro_by_id.get(recipe_id) or {}
                require(estimate.get("basis") == "planning-estimate-per-serving", f"candidate {recipe_id} lacks estimated per-serving macro basis in {path.name}", errors)
                for field in ("calories_kcal", "protein_g", "carbohydrates_g", "fat_g"):
                    require(isinstance(estimate.get(field), (int, float)) and estimate.get(field) >= 0, f"candidate {recipe_id} lacks valid {field} in {path.name}", errors)

        package_reconciliation_required = created_at >= "2026-09-13T00:00:00-04:00" and data.get("status") in {"awaiting-approval", "ordered", "completed"}
        if package_reconciliation_required:
            ingredient_plan = data.get("ingredient_plan") or []
            require(bool(ingredient_plan), f"finalized run lacks ingredient package reconciliation in {path.name}", errors)
            for item in ingredient_plan:
                ingredient = item.get("ingredient") or "unknown"
                for field in ("recipe_id", "recipe_quantity", "preparation_form", "pantry_quantity", "sku", "brand", "preferred_brand_check", "package_count", "net_quantity_per_package", "purchase_quantity", "allocation", "expected_remainder"):
                    require(field in item, f"ingredient {ingredient} lacks {field} in {path.name}", errors)
                require(isinstance(item.get("package_count"), int) and item.get("package_count") >= 0, f"ingredient {ingredient} has invalid package_count in {path.name}", errors)
                requires_review = item.get("package_count", 0) > 1 or item.get("full_package_excess") is True
                if requires_review:
                    require(bool(item.get("quantity_review")), f"ingredient {ingredient} lacks duplicate/excess quantity review in {path.name}", errors)

        receipt_required = created_at >= "2026-09-13T00:00:00-04:00" and (data.get("order") or {}).get("placed") is True
        if receipt_required:
            receipt = data.get("receipt") or {}
            receipt_status = receipt.get("status")
            require(receipt_status in {"captured", "unavailable"}, f"placed order lacks receipt status in {path.name}", errors)
            if receipt_status == "captured":
                require(bool(receipt.get("captured_at")), f"captured receipt lacks timestamp in {path.name}", errors)
                require(bool(receipt.get("source")), f"captured receipt lacks source in {path.name}", errors)
                require(bool(receipt.get("line_items")), f"captured receipt lacks line items in {path.name}", errors)
                require(receipt.get("reconciled_against_approved_cart") is True, f"captured receipt is not reconciled in {path.name}", errors)
                totals = receipt.get("totals") or {}
                require(isinstance(totals.get("charged_total"), (int, float)), f"captured receipt lacks charged total in {path.name}", errors)
            if receipt_status == "unavailable":
                require(bool(receipt.get("retrieval_attempts")), f"unavailable receipt lacks retrieval attempts in {path.name}", errors)
                require(bool(receipt.get("blocker")), f"unavailable receipt lacks blocker in {path.name}", errors)
                require((data.get("closeout") or {}).get("follow_up_needed") is True, f"unavailable receipt must remain open for follow-up in {path.name}", errors)
            if data.get("status") == "completed":
                require(receipt_status == "captured", f"completed order lacks preserved receipt in {path.name}", errors)

    run_template = documents.get(ROOT / "templates/run.yaml") or {}
    require(run_template.get("version") == 3, "run template must use deterministic state schema version 3", errors)
    require("session_id" in run_template, "run template must link to a chat session", errors)
    require("handoff" in run_template, "run template must include an explicit handoff", errors)
    selection_template = run_template.get("selection") or {}
    for field in ("revision", "status", "active_meal_ids", "updated_at", "history"):
        require(field in selection_template, f"run template selection lacks {field}", errors)
    require("selected_recipe_ids" not in (run_template.get("menu") or {}), "run template must not duplicate canonical selection under menu", errors)
    shopping_review = run_template.get("shopping_review") or {}
    require("presented_at" in shopping_review, "run template must timestamp the shopping review", errors)
    require("response_received_at" in shopping_review, "run template must record the shopping-review response", errors)
    require("cart_build_authorized" in shopping_review, "run template must record cart-build authorization", errors)
    require("pantry_exclusions" in shopping_review, "run template must capture pantry exclusions", errors)
    require("additional_items" in shopping_review, "run template must capture additional groceries", errors)
    require("confirmed_at" in shopping_review, "run template must gate cart building on shopping confirmation", errors)
    require("ingredient_plan" in run_template, "run template must capture recipe-to-cart package reconciliation", errors)
    require("ingredient_plan_revision" in run_template, "run template must version ingredient plans", errors)
    require("ingredient_plan_selection_revision" in run_template, "run template must bind ingredient plans to selection revisions", errors)
    require("selection_revision" in shopping_review, "run template shopping review must bind to a selection revision", errors)
    approval_template = run_template.get("approval") or {}
    for field in ("selection_revision", "cart_snapshot_id"):
        require(field in approval_template, f"run template approval lacks {field}", errors)
    recipe_cards = ((run_template.get("artifacts") or {}).get("recipe_cards"))
    require(isinstance(recipe_cards, list), "run template must track recipe-card generation and printing", errors)
    receipt_template = run_template.get("receipt") or {}
    for field in ("status", "captured_at", "source", "private_artifact", "line_items", "totals", "reconciled_against_approved_cart", "discrepancies", "retrieval_attempts", "blocker"):
        require(field in receipt_template, f"run template receipt lacks {field}", errors)
    require("sources" in (run_template.get("menu") or {}), "run template must capture recipe-source provenance", errors)
    require("macro_estimates" in (run_template.get("menu") or {}), "run template must capture candidate macro estimates", errors)
    interface_constraints = (run_template.get("context_snapshot") or {}).get("interface_constraints") or {}
    for field in ("primary_interface", "desktop_browser_visible_to_user", "chat_updates_required"):
        require(field in interface_constraints, f"run template interface constraints lack {field}", errors)

    session_template = documents.get(ROOT / "templates/session.yaml") or {}
    require(session_template.get("version") == 2, "session template must use deterministic handoff schema version 2", errors)
    require("handoff" in session_template, "session template must include an explicit handoff", errors)
    for field in ("id", "started_at", "closed_at", "status", "request_summary", "result_summary", "run_ids", "issue_ids", "change_ids", "outcome_ids", "artifact_paths", "timeline", "lessons", "follow_up", "privacy_reviewed"):
        require(field in session_template, f"session template lacks {field}", errors)

    card_template = ROOT / "templates" / "recipe-card.yaml"
    require(card_template.exists(), "missing structured recipe-card template", errors)

    availability = documents.get(ROOT / "registers/availability.yaml") or {}
    for observation in availability.get("observations", []):
        require(observation.get("retailer_id") in retailer_ids, f"unknown retailer in availability observation {observation.get('id')}", errors)

    outcomes = documents.get(ROOT / "registers/outcomes.yaml") or {}
    outcome_by_id = {}
    candidate_ids_by_run = {
        (documents.get(path) or {}).get("id"): set((((documents.get(path) or {}).get("menu") or {}).get("candidate_recipe_ids") or []))
        for path in sorted((ROOT / "runs").glob("*.yaml"))
    }
    for outcome in outcomes.get("outcomes", []):
        if outcome.get("id"):
            outcome_by_id[outcome["id"]] = outcome
        outcome_run_id = outcome.get("run_id")
        outcome_recipe_id = outcome.get("recipe_id")
        require(outcome_run_id in run_ids, f"unknown run in outcome {outcome.get('id')}", errors)
        known_recipe_or_candidate = outcome_recipe_id in recipe_ids or outcome_recipe_id in candidate_ids_by_run.get(outcome_run_id, set())
        require(known_recipe_or_candidate, f"unknown recipe or run candidate in outcome {outcome.get('id')}", errors)

    for recipe_id, recipe in recipe_documents.items():
        validation = recipe.get("validation") or {}
        outcome = outcome_by_id.get(validation.get("outcome_id"))
        require(outcome is not None, f"validated recipe lacks linked outcome: {recipe_id}", errors)
        if outcome:
            require(outcome.get("recipe_id") == recipe_id, f"recipe outcome mismatch: {recipe_id}", errors)
            require(outcome.get("run_id") == validation.get("run_id"), f"recipe run mismatch: {recipe_id}", errors)
            require(outcome.get("cooked") is True, f"validated recipe was not cooked: {recipe_id}", errors)
            require(outcome.get("repeat") is True, f"validated recipe lacks positive repeat decision: {recipe_id}", errors)

    issue_data = documents.get(ROOT / "registers/issues.yaml") or {}
    issue_ids = {item.get("id") for item in issue_data.get("issues", []) if item.get("id")}
    change_data = documents.get(ROOT / "registers/change-log.yaml") or {}
    change_ids = {item.get("id") for item in change_data.get("changes", []) if item.get("id")}
    outcome_ids = set(outcome_by_id)
    for session_id, session in session_documents.items():
        for run_id in session.get("run_ids") or []:
            require(run_id in run_ids, f"session {session_id} links unknown run {run_id}", errors)
        for issue_id in session.get("issue_ids") or []:
            require(issue_id in issue_ids, f"session {session_id} links unknown issue {issue_id}", errors)
        for change_id in session.get("change_ids") or []:
            require(change_id in change_ids, f"session {session_id} links unknown change {change_id}", errors)
        for outcome_id in session.get("outcome_ids") or []:
            require(outcome_id in outcome_ids, f"session {session_id} links unknown outcome {outcome_id}", errors)
        for artifact_path in session.get("artifact_paths") or []:
            require((ROOT / artifact_path).exists(), f"session {session_id} links missing artifact {artifact_path}", errors)

    for path in sorted((ROOT / "runs").glob("*.yaml")):
        run = documents.get(path) or {}
        if run.get("version", 1) >= 2 and run.get("session_id") in session_documents:
            linked_runs = session_documents[run["session_id"]].get("run_ids") or []
            require(run.get("id") in linked_runs, f"session {run['session_id']} does not link back to run {run.get('id')}", errors)

    private_path = ROOT / "local/private.yaml"
    require(not private_path.exists() or "local/private.yaml" in (ROOT / ".gitignore").read_text(encoding="utf-8"), "local/private.yaml must be ignored", errors)
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("Validation failed:")
        for failure in failures:
            print(f"- {failure}")
        sys.exit(1)
    print("Validation passed")
