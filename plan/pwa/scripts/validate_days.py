"""Validate all PWA itinerary data without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DAYS_DIR = ROOT / "days"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
STEP_TYPES = {"transit", "walk", "meal", "visit", "task", "break"}
BLOCK_TYPES = {"paragraph", "warning", "list"}
ITEM_TYPES = {"link", "image"}


def require_string(value: object, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_action(action: object, path: str, errors: list[str]) -> None:
    if not isinstance(action, dict):
        errors.append(f"{path} must be an object")
        return
    if action.get("type") not in ITEM_TYPES:
        errors.append(f"{path}.type must be link or image")
    require_string(action.get("label"), f"{path}.label", errors)
    if action.get("type") == "link" and not valid_url(action.get("url")):
        errors.append(f"{path}.url must be an http(s) URL")
    if action.get("type") == "image":
        require_string(action.get("imageLabel"), f"{path}.imageLabel", errors)
        require_string(action.get("src"), f"{path}.src", errors)
        src = action.get("src")
        if isinstance(src, str) and not (ROOT / src).resolve().is_file():
            errors.append(f"{path}.src does not exist: {src}")
    if "primary" in action and not isinstance(action["primary"], bool):
        errors.append(f"{path}.primary must be a boolean")


def validate_day(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        day = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.name}: cannot read JSON: {exc}"]

    prefix = path.name
    if not isinstance(day, dict):
        return [f"{prefix}: root must be an object"]

    if day.get("schemaVersion") != 1:
        errors.append(f"{prefix}: schemaVersion must be 1")
    if not DATE_RE.fullmatch(str(day.get("id", ""))):
        errors.append(f"{prefix}: id must use YYYY-MM-DD")
    if day.get("id") != path.stem:
        errors.append(f"{prefix}: id must match the filename")
    if day.get("date") != day.get("id"):
        errors.append(f"{prefix}: date must match id")

    for key in ("timeZone", "utcOffset", "eyebrow", "title", "subtitle", "footer"):
        require_string(day.get(key), f"{prefix}.{key}", errors)

    completion = day.get("completion")
    if not isinstance(completion, dict):
        errors.append(f"{prefix}.completion must be an object")
    else:
        for key in ("title", "time", "summary"):
            require_string(completion.get(key), f"{prefix}.completion.{key}", errors)

    preparation = day.get("preparation")
    if not isinstance(preparation, list):
        errors.append(f"{prefix}.preparation must be an array")
    else:
        prep_ids: set[str] = set()
        for index, item in enumerate(preparation):
            item_path = f"{prefix}.preparation[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not ID_RE.fullmatch(item_id):
                errors.append(f"{item_path}.id must be lowercase kebab-case")
            elif item_id in prep_ids:
                errors.append(f"{item_path}.id is duplicated")
            prep_ids.add(str(item_id))
            require_string(item.get("text"), f"{item_path}.text", errors)
            if "link" in item:
                link = item["link"]
                if not isinstance(link, dict) or not valid_url(link.get("url")):
                    errors.append(f"{item_path}.link must contain a valid URL")
                else:
                    require_string(link.get("label"), f"{item_path}.link.label", errors)

    steps = day.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append(f"{prefix}.steps must be a non-empty array")
    else:
        step_ids: set[str] = set()
        previous_start: datetime | None = None
        base_date = datetime.strptime(str(day.get("date")), "%Y-%m-%d") if DATE_RE.fullmatch(str(day.get("date", ""))) else None
        for index, step in enumerate(steps):
            step_path = f"{prefix}.steps[{index}]"
            if not isinstance(step, dict):
                errors.append(f"{step_path} must be an object")
                continue
            step_id = step.get("id")
            if not isinstance(step_id, str) or not ID_RE.fullmatch(step_id):
                errors.append(f"{step_path}.id must be lowercase kebab-case")
            elif step_id in step_ids:
                errors.append(f"{step_path}.id is duplicated")
            step_ids.add(str(step_id))

            if step.get("type") not in STEP_TYPES:
                errors.append(f"{step_path}.type is unsupported")
            for key in ("title", "kind", "summary"):
                require_string(step.get(key), f"{step_path}.{key}", errors)
            for key in ("start", "end"):
                if not TIME_RE.fullmatch(str(step.get(key, ""))):
                    errors.append(f"{step_path}.{key} must use HH:MM")
            if not isinstance(step.get("hardDeadline"), bool):
                errors.append(f"{step_path}.hardDeadline must be a boolean")

            if base_date and TIME_RE.fullmatch(str(step.get("start", ""))):
                start = datetime.combine(base_date.date(), datetime.strptime(step["start"], "%H:%M").time())
                if previous_start and start < previous_start:
                    start += timedelta(days=1)
                if previous_start and start < previous_start:
                    errors.append(f"{step_path} starts before the preceding step")
                previous_start = start

            blocks = step.get("blocks")
            if not isinstance(blocks, list):
                errors.append(f"{step_path}.blocks must be an array")
            else:
                for block_index, block in enumerate(blocks):
                    block_path = f"{step_path}.blocks[{block_index}]"
                    if not isinstance(block, dict) or block.get("type") not in BLOCK_TYPES:
                        errors.append(f"{block_path} has an unsupported type")
                    elif block["type"] == "list":
                        if not isinstance(block.get("items"), list) or not block["items"]:
                            errors.append(f"{block_path}.items must be a non-empty array")
                    else:
                        require_string(block.get("text"), f"{block_path}.text", errors)

            actions = step.get("actions")
            if not isinstance(actions, list):
                errors.append(f"{step_path}.actions must be an array")
            else:
                for action_index, action in enumerate(actions):
                    validate_action(action, f"{step_path}.actions[{action_index}]", errors)

    resources = day.get("resources")
    if not isinstance(resources, list):
        errors.append(f"{prefix}.resources must be an array")
    else:
        for index, resource in enumerate(resources):
            resource_path = f"{prefix}.resources[{index}]"
            validate_action(resource, resource_path, errors)
            if isinstance(resource, dict):
                require_string(resource.get("description"), f"{resource_path}.description", errors)

    return errors


def main() -> int:
    files = sorted(DAYS_DIR.glob("*.json"))
    if not files:
        print("No day files found.", file=sys.stderr)
        return 1

    errors = [error for path in files for error in validate_day(path)]
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1

    print(f"Validated {len(files)} day file(s): {', '.join(path.stem for path in files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
