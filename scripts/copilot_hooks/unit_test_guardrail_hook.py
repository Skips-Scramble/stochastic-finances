#!/usr/bin/env python3
"""PostToolUse hook that enforces basic unit-test assertion guardrails.

This hook inspects tool payloads for edits to test files. If a new test file appears
without any obvious assertion token, it requests a block so low-value tests are not
silently accepted.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

TEST_FILE_RE = re.compile(
    r"(^|[\\/])(tests?[\\/].*|test_.*\.py|.*[\\/]tests\.py)$", re.IGNORECASE
)
ASSERT_RE = re.compile(r"\b(assert\s+|self\.assert\w+\s*\()")
EXCLUDED_TEST_FILES = {"conftest.py"}


def _read_event() -> dict[str, Any]:
    try:
        raw = sys.stdin.read().strip()
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}


def _print_continue(system_message: str | None = None) -> None:
    payload: dict[str, Any] = {"continue": True}
    if system_message:
        payload["systemMessage"] = system_message
    print(json.dumps(payload))


def _print_block(reason: str) -> None:
    payload = {
        "continue": False,
        "stopReason": reason,
        "systemMessage": reason,
        "decision": "block",
    }
    print(json.dumps(payload))


def _extract_text(event: dict[str, Any]) -> str:
    # We use a broad extraction approach because payload shape may vary by tool.
    chunks: list[str] = []
    for key in (
        "toolInput",
        "toolOutput",
        "result",
        "payload",
        "text",
        "message",
        "command",
        "input",
    ):
        value = event.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            chunks.append(value)
        else:
            chunks.append(json.dumps(value, ensure_ascii=True))
    chunks.append(json.dumps(event, ensure_ascii=True))
    return "\n".join(chunks)


def _looks_like_test_edit(text: str) -> bool:
    paths = re.findall(r"[A-Za-z0-9_./\\-]+\.py", text)
    for path in paths:
        lowered = path.lower()
        if lowered.endswith(tuple(EXCLUDED_TEST_FILES)):
            continue
        if TEST_FILE_RE.search(path):
            return True
    return False


def _has_assertions(text: str) -> bool:
    return bool(ASSERT_RE.search(text))


def main() -> int:
    event = _read_event()

    event_name = str(event.get("hookEventName") or event.get("eventName") or "")
    if event_name and event_name != "PostToolUse":
        _print_continue()
        return 0

    text = _extract_text(event)
    if not _looks_like_test_edit(text):
        _print_continue()
        return 0

    if _has_assertions(text):
        _print_continue(
            "Unit-test guardrail check passed: assertions detected in test edit."
        )
        return 0

    _print_block(
        "Unit-test guardrail blocked this change: test edits were detected without clear assertions. "
        "Add meaningful assertions or update the hook if this file is not a test case."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
