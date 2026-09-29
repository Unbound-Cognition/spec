#!/usr/bin/env python3
"""Open Cognitive Memory Specification — Schema & Conformance Validator.

Validates that all JSON schemas are well-formed and tests sample fixtures against
their constraints without external dependencies.
"""

from __future__ import annotations

import json
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "schemas"


def validate_schema_json(path: Path) -> dict:
    """Ensure schema file is valid JSON and contains standard Draft 2020-12 header."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "$schema" in data, f"{path.name} missing $schema"
    assert "$id" in data, f"{path.name} missing $id"
    return data


def validate_sample_memory(memory_schema: dict) -> None:
    sample = {
        "id": str(uuid.uuid4()),
        "content": "Knot DNS daemon handles auth zones on cute-vps over port 53.",
        "layer": "semantic",
        "memory_type": "fact",
        "status": "active",
        "importance": 0.85,
        "trust": 1.0,
        "surprise": 0.42,
        "tags": ["dns", "knot", "infrastructure"],
        "temporal": {
            "created_at": 1789957124000,
            "updated_at": 1789957124000,
            "fact_date": "2026-09-21",
            "last_accessed_at": 1789957124000,
            "access_count": 3,
            "previous_memory_id": None,
            "causal_parent_id": None,
        },
    }
    # Validate required fields
    for req in memory_schema["required"]:
        assert req in sample, f"Sample memory missing required field: {req}"

    # Validate enums
    assert sample["layer"] in memory_schema["properties"]["layer"]["enum"]
    assert sample["memory_type"] in memory_schema["properties"]["memory_type"]["enum"]
    assert sample["status"] in memory_schema["properties"]["status"]["enum"]
    assert 0.0 <= sample["importance"] <= 1.0


def validate_sample_checkpoint(checkpoint_schema: dict) -> None:
    sample = {
        "project_id": "/Users/ari/projects/spec",
        "task": "scaffold open cognitive spec",
        "summary": "Completed core architecture, data model, retrieval, and wire protocol docs.",
        "status": "in_progress",
        "decisions": [
            "Used JSONL + MCP dual transport standard",
            "Separated procedural memory from episodic logs",
        ],
        "next_steps": [
            "Write zero-knowledge sync protocol spec",
            "Add JSON schemas for validation",
        ],
        "blockers": [],
        "key_files": ["README.md", "schemas/memory.schema.json"],
        "timestamp": 1789957124000,
    }
    for req in checkpoint_schema["required"]:
        assert req in sample, f"Sample checkpoint missing required field: {req}"
    assert sample["status"] in checkpoint_schema["properties"]["status"]["enum"]


def validate_sample_sync_envelope(sync_schema: dict) -> None:
    sample = {
        "event_id": str(uuid.uuid4()),
        "memory_id": str(uuid.uuid4()),
        "device_id": "aris-macbook-air",
        "sequence": 1420,
        "timestamp": 1790584400000,
        "operation": "upsert",
        "crypto": {
            "algorithm": "ChaCha20-Poly1305",
            "key_id": "primary",
            "nonce": "d8f92a4b1c8e034f5a6b7c8d",
            "ciphertext": "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY=",
            "tag": "MTIzNDU2Nzg5MDEyMzQ1Ng==",
        },
    }
    for req in sync_schema["required"]:
        assert req in sample, f"Sample sync envelope missing required field: {req}"
    assert sample["operation"] in sync_schema["properties"]["operation"]["enum"]
    assert sample["crypto"]["algorithm"] in sync_schema["properties"]["crypto"]["properties"]["algorithm"]["enum"]


def main() -> int:
    print("Validating Open Cognitive Memory schemas...")
    schema_files = list(SCHEMAS_DIR.glob("*.json"))
    if not schema_files:
        print(f"Error: no schema files found in {SCHEMAS_DIR}", file=sys.stderr)
        return 1

    schemas = {}
    for sf in sorted(schema_files):
        try:
            schemas[sf.name] = validate_schema_json(sf)
            print(f"  [PASS] {sf.name} is valid JSON schema")
        except Exception as e:
            print(f"  [FAIL] {sf.name}: {e}", file=sys.stderr)
            return 1

    print("\nValidating sample fixtures against schema rules...")
    try:
        validate_sample_memory(schemas["memory.schema.json"])
        print("  [PASS] memory.schema.json fixture valid")

        validate_sample_checkpoint(schemas["checkpoint.schema.json"])
        print("  [PASS] checkpoint.schema.json fixture valid")

        validate_sample_sync_envelope(schemas["sync-envelope.schema.json"])
        print("  [PASS] sync-envelope.schema.json fixture valid")
    except Exception as e:
        print(f"  [FAIL] fixture validation error: {e}", file=sys.stderr)
        return 1

    print("\nAll specification schemas and fixtures verified successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
