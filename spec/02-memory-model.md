# 02. memory model

this document defines the canonical record envelope, metadata fields, scoring metrics, and relationship graph structures.

## 1. the memory envelope

every stored memory record conforms to the following schema:

```json
{
  "id": "019dca9f-7d01-7c33-981e-722195058d48",
  "content": "Contabo S3 storage should not be mounted directly under Steam Library paths; remote FUSE I/O stalls game downloads.",
  "layer": "procedural",
  "memory_type": "procedure",
  "status": "active",
  "importance": 0.85,
  "trust": 1.0,
  "surprise": 0.62,
  "tags": ["steam", "rclone", "storage", "performance"],
  "entities": [
    {"name": "Steam", "type": "software"},
    {"name": "Contabo", "type": "service"}
  ],
  "temporal": {
    "created_at": 1790584400000,
    "updated_at": 1790584400000,
    "fact_date": null,
    "last_accessed_at": 1790584400000,
    "access_count": 1,
    "previous_memory_id": "019dca9e-6c00-7c22-871d-612084047b31",
    "causal_parent_id": null
  },
  "provenance": {
    "source": "user_explicit",
    "project_id": "/Users/ari/Ash/engram",
    "session_id": "862fec72-aeaf-4ea6-b349-d045e09ec9e5",
    "author": "ari"
  }
}
```

---

## 2. field definitions

### core fields
- **`id`** *(string, required)*: unique identifier (UUIDv4 or KSUID).
- **`content`** *(string, required)*: the substantive payload in plain markdown. must be dense and self-contained.
- **`layer`** *(string, required)*: one of `["working", "episodic", "semantic", "procedural", "codebase"]`.
- **`memory_type`** *(string, required)*: one of `["fact", "procedure", "narrative", "negative"]`.
- **`status`** *(string, required)*: one of `["active", "challenged", "superseded", "forgotten"]`.

### scoring & dynamics
- **`importance`** *(float 0.0 - 1.0)*: intrinsic value of the memory. higher for structural decisions, security rules, and user preferences; lower for transient chat.
- **`trust`** *(float 0.0 - 1.0)*: confidence in the source. direct user statements = 1.0; automated background LLM extractions = 0.6–0.8.
- **`surprise`** *(float 0.0 - 1.0)*: computed at ingest time. measures semantic distance from existing near-neighbors. high surprise boosts novelty retention; low surprise flags redundancy.

### temporal backbone
- **`created_at`** *(integer, ms)*: epoch timestamp when the record was saved.
- **`fact_date`** *(string ISO-8601 or null)*: the real-world date the memory refers to, if distinct from creation time (e.g. *"2026-03-24"*).
- **`previous_memory_id`** *(string or null)*: linear predecessor in the episodic chain. allows $O(1)$ chronological traversal forward and backward.
- **`causal_parent_id`** *(string or null)*: links a reaction or fix to the error or trigger that caused it.

---

## 3. entity graph & relationships

memories do not float in isolation. entities mentioned in memories form an associative graph:

### entity schema
```json
{
  "name": "cute-vps",
  "canonical_name": "cute-vps",
  "entity_type": "infrastructure",
  "aliases": ["15.135.202.14", "ip-172-31-1-89"]
}
```

### relationship schema
```json
{
  "source_entity": "raya.ac",
  "target_entity": "vmi3253649",
  "relationship_type": "hosted_on",
  "confidence": 1.0,
  "observed_at": 1790584400000
}
```

standard relationship types:
- `depends_on`
- `hosted_on`
- `authored_by`
- `contradicts`
- `supersedes`
- `relates_to`

conforming retrieval engines use 1-hop graph traversal to discover associated context even when lexical or dense embedding matches miss.
