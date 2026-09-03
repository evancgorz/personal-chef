from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_RUN_STATES = {
    "draft",
    "menu-presented",
    "meals-selected",
    "cart-building",
    "comparison-ready",
    "awaiting-approval",
    "ordered",
    "completed",
    "cancelled",
    "blocked",
}


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate() -> list[str]:
    errors: list[str] = []
    required = [
        ROOT / "AGENTS.md",
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

    yaml_paths = sorted(
        p
        for directory in ("registers", "recipes", "runs", "templates")
        for p in (ROOT / directory).glob("*.yaml")
    )
    documents = {}
    for path in yaml_paths:
        try:
            documents[path] = load_yaml(path)
        except Exception as exc:
            errors.append(f"invalid YAML in {path.relative_to(ROOT)}: {exc}")

    recipe_ids: set[str] = set()
    for path in sorted((ROOT / "recipes").glob("*.yaml")):
        data = documents.get(path) or {}
        recipe_id = data.get("id")
        require(isinstance(recipe_id, str) and bool(KEBAB.fullmatch(recipe_id)), f"invalid recipe id in {path.name}", errors)
        if isinstance(recipe_id, str):
            require(recipe_id not in recipe_ids, f"duplicate recipe id: {recipe_id}", errors)
            recipe_ids.add(recipe_id)
        require(data.get("canonical_yield", 0) > 0, f"canonical_yield must be positive in {path.name}", errors)
        total = (data.get("time") or {}).get("total_minutes")
        require(isinstance(total, (int, float)) and total > 0, f"total_minutes must be positive in {path.name}", errors)
        require(bool(data.get("ingredients")), f"recipe has no ingredients: {path.name}", errors)
        require(bool(data.get("instructions")), f"recipe has no instructions: {path.name}", errors)

    retailer_data = documents.get(ROOT / "registers/retailers.yaml") or {}
    retailer_ids = {item.get("id") for item in retailer_data.get("retailers", []) if item.get("id")}
    for retailer_id in retailer_ids:
        require(bool(KEBAB.fullmatch(retailer_id)), f"invalid retailer id: {retailer_id}", errors)

    run_ids: set[str] = set()
    for path in sorted((ROOT / "runs").glob("*.yaml")):
        data = documents.get(path) or {}
        run_id = data.get("id")
        require(isinstance(run_id, str) and bool(KEBAB.fullmatch(run_id)), f"invalid run id in {path.name}", errors)
        if isinstance(run_id, str):
            require(run_id not in run_ids, f"duplicate run id: {run_id}", errors)
            run_ids.add(run_id)
        require(data.get("status") in VALID_RUN_STATES, f"invalid run status in {path.name}", errors)
        selected = ((data.get("menu") or {}).get("selected_recipe_ids") or [])
        for recipe_id in selected:
            require(recipe_id in recipe_ids, f"unknown recipe {recipe_id} in {path.name}", errors)

    availability = documents.get(ROOT / "registers/availability.yaml") or {}
    for observation in availability.get("observations", []):
        require(observation.get("retailer_id") in retailer_ids, f"unknown retailer in availability observation {observation.get('id')}", errors)

    outcomes = documents.get(ROOT / "registers/outcomes.yaml") or {}
    for outcome in outcomes.get("outcomes", []):
        require(outcome.get("recipe_id") in recipe_ids, f"unknown recipe in outcome {outcome.get('id')}", errors)
        require(outcome.get("run_id") in run_ids, f"unknown run in outcome {outcome.get('id')}", errors)

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

