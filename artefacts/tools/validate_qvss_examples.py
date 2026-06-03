#!/usr/bin/env python3

from pathlib import Path
import json
import sys
from typing import Any, Dict, Iterable, List, Set, Tuple

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("Install dependencies with: pip install pyyaml jsonschema")


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "qvss-1.0.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text())
VALIDATOR = Draft202012Validator(SCHEMA)

NUMERIC_OPS = {"<", "<=", ">", ">="}
RULE_SECTIONS = ("rules", "filters", "criteria")


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open() as handle:
        obj = yaml.safe_load(handle)
    if not isinstance(obj, dict):
        raise ValueError(f"{path}: expected a YAML mapping at document root")
    return obj


def rule_names(obj: Dict[str, Any]) -> Set[str]:
    names: Set[str] = set()
    for section in RULE_SECTIONS:
        rules = obj.get(section) or {}
        if isinstance(rules, dict):
            names.update(rules.keys())
    return names


def iter_rule_objects(obj: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    for section in RULE_SECTIONS:
        rules = obj.get(section) or {}
        if not isinstance(rules, dict):
            continue

        for rule_name, rule in rules.items():
            if isinstance(rule, dict):
                yield f"{section}.{rule_name}", rule
                yield from iter_conditions(f"{section}.{rule_name}", rule)


def iter_conditions(prefix: str, rule: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    conditions = rule.get("conditions") or []
    if not isinstance(conditions, list):
        return

    for i, condition in enumerate(conditions):
        path = f"{prefix}.conditions[{i}]"
        if isinstance(condition, dict):
            yield path, condition
            yield from iter_conditions(path, condition)


def has_rule_bearing_section(obj: Dict[str, Any]) -> bool:
    for section in RULE_SECTIONS:
        rules = obj.get(section)
        if isinstance(rules, dict) and len(rules) > 0:
            return True
    return False


def is_numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def semantic_errors(obj: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    status = obj.get("status")
    if status not in {"deprecated", "withdrawn"} and not has_rule_bearing_section(obj):
        errors.append("non-deprecated QV set must contain at least one of rules, filters, or criteria")

    names = rule_names(obj)
    qualification = obj.get("qualification") or {}
    if isinstance(qualification, dict):
        qualification_rule = qualification.get("rule")
        if qualification_rule and qualification_rule not in names:
            errors.append(f"qualification.rule {qualification_rule!r} does not refer to a declared rule")

    for path, rule in iter_rule_objects(obj):
        operator = rule.get("operator")
        datatype = rule.get("datatype")
        value = rule.get("value")
        logic = rule.get("logic")
        conditions = rule.get("conditions")

        if operator == "not_contains":
            errors.append(f"{path}: not_contains is not a core QVSS operator; use not around contains")

        if operator in NUMERIC_OPS and datatype in {"number", "integer"} and not is_numeric(value):
            errors.append(f"{path}: numeric operator {operator!r} requires a numeric value")

        if logic == "not":
            if not isinstance(conditions, list) or len(conditions) != 1:
                errors.append(f"{path}: logic 'not' requires exactly one condition")

        ref = rule.get("ref")
        if ref and ref not in names:
            errors.append(f"{path}: ref {ref!r} does not refer to a declared rule")

    return errors


def validate_file(path: Path) -> Tuple[List[Any], List[str]]:
    obj = load_yaml(path)
    schema_errors = sorted(VALIDATOR.iter_errors(obj), key=lambda e: list(e.path))
    sem_errors = semantic_errors(obj)
    return schema_errors, sem_errors


def print_schema_error(err: Any) -> str:
    location = ".".join(str(x) for x in err.path)
    if location:
        return f"{location}: {err.message}"
    return err.message


def main() -> None:
    ok = True

    valid_dir = ROOT / "examples" / "valid"
    invalid_dir = ROOT / "examples" / "invalid"

    for path in sorted(valid_dir.glob("*.yaml")):
        schema_errors, sem_errors = validate_file(path)

        if schema_errors or sem_errors:
            ok = False
            print(f"FAIL valid example: {path.relative_to(ROOT)}")
            for err in schema_errors:
                print(f"  schema: {print_schema_error(err)}")
            for err in sem_errors:
                print(f"  semantic: {err}")
        else:
            print(f"OK valid: {path.relative_to(ROOT)}")

    for path in sorted(invalid_dir.glob("*.yaml")):
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
