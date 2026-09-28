# 04. wire protocol

this document defines the standard transports, operations, and tool contracts for agents and desktop hosts communicating with a local cognitive engine.

## 1. transports

a conforming cognitive engine must support at least one of the following transports:

1. **native JSONL (stdio)**:
   - standard input / output stream.
   - one JSON payload per line.
   - zero network port binding; maximum security on local workstations.
2. **Model Context Protocol (MCP)**:
   - standard JSON-RPC 2.0 transport over stdio or SSE.
   - allows plug-and-play integration with Claude Code, Codex, Cursor, Windsurf, and custom AI clients.
3. **local HTTP / SSE daemon**:
   - loopback-only binding (default `127.0.0.1:8420`).
   - REST endpoints for web workspaces, status dashboards, and non-stdio clients.

---

## 2. core operations

### `search`
runs hybrid 5-channel retrieval across the store.
```json
// request
{
  "operation": "search",
  "query": "how did we fix the steam download stall?",
  "top_k": 5
}

// response
{
  "status": "ok",
  "results": [
    {
      "id": "019dca9f-7d01-7c33-981e-722195058d48",
      "content": "Contabo S3 storage should not be mounted directly under Steam Library paths; remote FUSE I/O stalls game downloads.",
      "layer": "procedural",
      "score": 0.942,
      "sources": {"dense": 2, "bm25": 1, "graph": 0}
    }
  ]
}
```

### `remember`
stores a new memory with automatic novelty/surprise gating.
```json
// request
{
  "operation": "remember",
  "content": "Knot DNS daemon uses LMDB backend and consumes ~12MB RAM on cute-vps.",
  "layer": "semantic",
  "memory_type": "fact",
  "tags": ["dns", "knot", "infrastructure"]
}

// response
{
  "status": "stored",
  "id": "019dca9f-7d01-7c33-981e-722195058d49",
  "surprise": 0.78,
  "importance": 0.80
}
```

### `session_checkpoint` & `session_resume`
standardized cross-agent handoffs. ensures that if a session in Claude Code is interrupted, a session in Codex or a local model can pick up the exact open loops.
```json
// session_checkpoint request
{
  "operation": "session_checkpoint",
  "project_id": "/Users/ari/projects/spec",
  "task": "scaffold open cognitive spec",
  "summary": "Completed core architecture, data model, retrieval, and wire protocol docs.",
  "decisions": [
    "Used JSONL + MCP dual transport standard",
    "Separated procedural memory from episodic logs"
  ],
  "next_steps": [
    "Write zero-knowledge sync protocol spec",
    "Add JSON schemas for validation"
  ],
  "blockers": []
}
```

---

## 3. MCP standard tools

for MCP-compliant environments, the engine exposes the following canonical tools:

- **`recall`**: fast, lightweight retrieval of recent project state.
- **`search`**: deep hybrid retrieval across the entire knowledge base.
- **`remember`**: stores facts, procedures, or narratives.
- **`remember_decision`**: stores architectural choices and rationales directly into the procedural layer.
- **`remember_error`**: stores error signatures and verified fixes.
- **`remember_negative`**: stores explicit assertions of non-existence to block hallucinations.
- **`drift_check`**: runs filesystem / reality verification against stored paths.
