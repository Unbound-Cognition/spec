# 06. conformance suite

this document specifies the test cases and validation requirements an engine must satisfy to be certified as a conforming implementation of the Open Cognitive Memory Specification.

## 1. conformance levels

conformance is evaluated across three tiers:

- **Level 1 (Core Storage & Schema)**: Implements the cognitive memory envelope (`memory.schema.json`), layer classification, and basic CRUD operations.
- **Level 2 (Retrieval Contract)**: Implements multi-channel retrieval, intent-aware RRF dynamic weighting, and confidence threshold noise gating (`query.schema.json`).
- **Level 3 (Sovereign Replication)**: Implements ChaCha20-Poly1305 zero-knowledge encryption, Lamport clock ordering, LWW reconciliation, and tombstone propagation (`sync-envelope.schema.json`).

---

## 2. normative test cases

### test group A: memory model & envelope
1. **envelope validation**:
   - MUST reject any memory record missing `id`, `content`, `layer`, `memory_type`, `status`, `importance`, or `temporal`.
   - MUST validate that `layer` is one of `working`, `episodic`, `semantic`, `procedural`, `codebase`.
   - MUST validate that `importance` is bounded in $[0.0, 1.0]$.
2. **temporal linkage**:
   - Updating a memory MUST update `temporal.updated_at` without mutating original `temporal.created_at`.
   - When a memory is revised, the new record MUST point to the previous record via `temporal.previous_memory_id`.

### test group B: retrieval contract
1. **exact keyword preservation**:
   - Queries with technical identifiers (e.g. `PercentIdleTime`, `0x80070005`, `uvicorn.workers`) MUST rank exact lexical matches above general semantic similarity.
2. **intent classification & procedural boost**:
   - Queries prefixed with "how to" or asking for debugging instructions MUST apply the procedural boost ($2.0\times$) to memories in the `procedural` layer.
3. **noise threshold gate**:
   - For adversarial or nonsense queries with zero relevance, the engine MUST return an empty result list (`results: []`) rather than injecting low-confidence matches ($score < 0.35$).

### test group C: zero-knowledge replication
1. **zero-plaintext leak**:
   - An exported sync envelope MUST NOT contain unencrypted occurrences of the memory text or raw float embeddings in plaintext.
2. **authenticated encryption integrity**:
   - Any modification of a single bit in the `ciphertext`, `nonce`, or `tag` MUST trigger an authentication failure and reject the event.
3. **tombstone propagation**:
   - Applying a `delete` or `tombstone` envelope for memory $M$ on an offline peer MUST transition $M$ to `forgotten` state upon synchronization, rather than resurrecting the record from local cache.
4. **causal fork preservation**:
   - If two devices record substantive concurrent edits to the same memory ID, the implementation MUST NOT discard either edit silently; the conflicting edit MUST be preserved with `causal_parent` link.

---

## 3. automated validation

conformance is validated across two test suites:

### 3.1 static schema & fixture validation
verifies that all JSON schemas conform to Draft 2020-12 and validates sample payloads without external dependencies:

```bash
python scripts/validate.py
```

### 3.2 live engine conformance runner
executes the normative test suite against any running engine implementing the wire protocol (Levels 1, 2, and 3):

```bash
# test a local engine daemon
python scripts/test_engine.py --url http://127.0.0.1:8420

# test an engine with bearer auth enabled
python scripts/test_engine.py --url http://my-vps:8420 --token <my-token>
```
