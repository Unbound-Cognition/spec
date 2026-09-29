# open cognitive memory specification

the open standard for sovereign, local-first agent memory and continuity.

## why this exists

most modern agent memory systems are either:
1. **flat vector stores** that lose structure, recency, and the distinction between facts, procedures, and stories.
2. **cloud-walled silos** where your agent's continuity is owned, monitored, and paywalled by a single vendor.

this specification defines a standard data model, wire protocol, and sync architecture for local-first agent memory. an implementation that conforms to this spec allows any AI agent (running locally or via API) to query and write to a permanent cognitive store that outlives the conversation and the model.

## core requirements

- **local-first storage**: memories live in open, standard databases (SQLite, Postgres). no mandatory remote telemetry or cloud dependencies.
- **multi-layer separation**: distinct cognitive layers for working context, episodic history, semantic knowledge, and procedural instructions.
- **lifecycle transparency**: memories can be active, challenged, superseded, or forgotten. retrieval is not proof of truth.
- **model-agnostic handoffs**: standardized checkpointing so sessions can resume across different models (e.g. starting in Claude, resuming in local Qwen/Llama) without losing context.
- **zero-knowledge sync**: protocol for synchronizing encrypted memory states across multiple personal devices without exposing plaintext or raw vector embeddings to intermediate sync relays.

## technical white paper

- **[sovereign cognitive substrate: a technical white paper](whitepaper.md)** — full architecture, retrieval mathematics, failure modes, and zero-knowledge replication protocol.

## specification structure

- **[01. core architecture](spec/01-core-architecture.md)** — memory layers, cognitive lifecycle, and threat model.
- **[02. memory model](spec/02-memory-model.md)** — data schemas, envelope format, importance scoring, and relationship graphs.
- **[03. retrieval contract](spec/03-retrieval-contract.md)** — multi-channel retrieval, intent weighting, and reranking expectations.
- **[04. wire protocol](spec/04-wire-protocol.md)** — JSONL native API, MCP tool definitions, and runtime hooks.
- **[05. zero-knowledge sync](spec/05-zero-knowledge-sync.md)** — encrypted delta logs, CRDT conflict resolution, and peer discovery.
- **[06. conformance suite](spec/06-conformance-suite.md)** — normative test cases and automated validation.
- **[schemas/](schemas/)** — formal JSON Schemas for validation.

## status

draft v0.1.0. referenced by [engram](https://github.com/Unbound-Cognition/engram) and [engram-desktop](https://github.com/Unbound-Cognition/engram-desktop).

## license

MIT
