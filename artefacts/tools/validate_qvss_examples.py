#!/usr/bin/env python3
from pathlib import Path
import json
import sys

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:
    sys.exit("Install dependencies with: pip install pyyaml jsonschema")

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "qvss-1.0.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)

NUMERIC_OPS = {"<", "<=", ">", ">="}

def load_yaml(path):
    with path.open() as handle:
        return yaml.safe_load(handle)

def iter_rules(obj):
    for section in ("rules", "filters", "criteria"):
        for name, rule in (obj.get(section) or {}).items():
            yield f"{section}.{name}", rule
            for i, condition in enumerate(rule.get("conditions") or []):
                yield f"{section}.{name}.conditions[{i}]", condition

def semantic_errors(obj):
    errors = []
    for name, rule in iter_rules(obj):
        operator = rule.get("operator")
        datatype = rule.get("datatype")
        value = rule.get("value")
        if operator in NUMERIC_OPS and datatype in {"number", "integer"} and not isinstance(value, (int, float)):
            errors.append(f"{name}: numeric operator {operator!r} requires a numeric value")
        if operator == "not_contains":
            errors.append(f"{name}: not_contains is not a core QVSS operator; use not around contains")
    return errors

def validate_file(path):
    obj = load_yaml(path)
    schema_errors = sorted(VALIDATOR.iter_errors(obj), key=lambda e: list(e.path))
    sem_errors = semantic_errors(obj)
    return schema_errors, sem_errors

def main():
    ok = True
    for path in sorted((ROOT / "examples" / "valid").glob("*.yaml")):
        schema_errors, sem_errors = validate_file(path)
        if schema_errors or sem_errors:
            ok = False
            print(f"FAIL valid example: {path.relative_to(ROOT)}")
            for err in schema_errors:
                print(f"  schema: {err.message}")
            for err in sem_errors:
                print(f"  semantic: {err}")
        else:
            print(f"OK valid: {path.relative_to(ROOT)}")

    for path in sorted((ROOT / "examples" / "invalid").glob("*.yaml")):
        schema_errors, sem_errors = validate_file(path)
        if schema_errors or sem_errors:
            print(f"OK invalid rejected: {path.relative_to(ROOT)}")
        else:
            ok = False
            print(f"FAIL invalid accepted: {path.relative_to(ROOT)}")

    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
