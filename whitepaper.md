# sovereign cognitive substrate: a technical white paper on local-first agent continuity

**author:** ari  
**organization:** unbound cognition  
**version:** draft 0.1.0  
**date:** september 2026  

---

## 1. why i built this

most modern agent memory systems are broken in one of two ways.

the first is the commercial cloud silo. major AI providers offer memory features that store your interaction history inside proprietary cloud databases. your agent's continuity is trapped behind closed API endpoints. if you change model providers, run a local model, work offline, or terminate a subscription, your agent's memory disappears. you don't own the data, you can't inspect the raw retrieval pipeline, and you can't verify what is retained or deleted.

the second is the naive vector store. many open-source projects attempt to solve agent memory by chunking session logs, embedding them with a sentence transformer, dumping them into a flat vector database, and doing top-k cosine similarity on user queries. in practice, this breaks down quickly:
- it loses exact keywords, function names, and specific error codes that dense vector spaces blur.
- it has no concept of time—asking "what did we decide yesterday?" retrieves semantically similar decisions from three months ago.
- it treats every stored chunk as permanent, immutable truth, even when subsequent work proves that fact wrong.
- it treats all information identically: a transient error log, an architectural decision, an executable procedure, and an episodic narrative are all flattened into the same vector soup.

i built engram and started the unbound cognition specification to solve this. the goal is simple: an open, local-first cognitive substrate where memory belongs to the person running the system, outlives any single conversation or model, and behaves more like an organized working memory than a dumb text dump.

this paper describes the architecture, retrieval mathematics, lifecycle rules, and zero-knowledge replication protocol that make this work.

---

## 2. failure modes of existing agent memory

to design a reliable cognitive system, you first have to understand the specific ways naive memory systems fail in real engineering workflows.

### 2.1 the cloud lock-in trap
when memory lives in a vendor's cloud, continuity becomes a subscription feature. the vendor decides how long memories persist, what gets filtered, and how relevance is ranked. if an engineer uses Claude for architecture, Codex for terminal execution, and a local Qwen model on an air-gapped machine, context does not travel between them. the engineer is forced to re-explain the project from scratch in every new tool.

### 2.2 the flat vector fallacy
single-vector cosine similarity search operates on broad semantic proximity. in practice, software engineering and deep knowledge work rely heavily on exact identifiers:
- searching for error code `0x80070005` or variable `PercentIdleTime` often produces low cosine similarity against relevant memories because the tokenizer splits unfamiliar tokens into meaningless subword fragments.
- cosine distance in high dimensions suffers from hubness problems, where certain vector hubs appear close to queries regardless of semantic relevance.
- vector distance alone provides no signal on whether an observation is primary evidence or a passing guess.

### 2.3 the permanence illusion
in human thinking and real software systems, facts change:
- a database configuration that was optimal in March is discarded in June.
- an external API endpoint changes its authentication scheme.
- an initial hypothesis about a bug is disproven by subsequent testing.

standard retrieval-augmented generation (RAG) stores text chunks indefinitely. when an agent queries the store, it retrieves the outdated fact alongside the current fact. the model is then forced to guess which contradictory claim is valid, often hallucinating a blend of both. without an explicit memory lifecycle (states like `challenged`, `superseded`, and `forgotten`), memory stores accumulate toxic prompt pollution over time.

---

## 3. the cognitive layer model

human cognition does not store every sensory input in one undifferentiated pile. it separates working memory, episodic recollections of events, semantic models of how the world works, and procedural rules for doing things.

unbound cognition formalizes this into five distinct cognitive layers:

```
+-------------------------------------------------------------+
| L0: Working Memory (active session buffers, current loops)  |
+-------------------------------------------------------------+
                              | distillation
                              v
+-------------------------------------------------------------+
| L1: Episodic Memory (narrative history, chronological logs) |
+-------------------------------------------------------------+
                              | abstraction
                              v
+-------------------------------------------------------------+
| L2: Semantic Memory (facts, entities, conceptual graphs)    |
+-------------------------------------------------------------+
                              | operationalization
                              v
+-------------------------------------------------------------+
| L3: Procedural Memory (executable workflows, error fixes)   |
+-------------------------------------------------------------+
                              | inspection
                              v
+-------------------------------------------------------------+
| Codebase Memory (AST symbols, file boundaries, project map) |
+-------------------------------------------------------------+
```

### L0: working context
ephemeral state for the active task. holds in-progress goals, active shell commands, and current blockers. when a session finishes, working memory is checkpointed and cleared.

### L1: episodic memory
chronological records of events and experiences. stores session summaries, diagnostic traces, and conversation narratives. every episodic record includes exact timestamps, causal predecessors, and session identifiers.

### L2: semantic memory
structured, objective knowledge about people, systems, tools, and environments. examples: *"Knot DNS daemon runs on cute-vps and listens on port 53"*. semantic memories link directly into an entity relationship graph.

### L3: procedural memory
the most valuable layer for autonomous agents. stores executable procedures, architectural decisions, and error-recovery patterns. when an agent spends two hours diagnosing a kernel panic or an FUSE mount deadlock, the distilled fix is stored here. on future runs, the agent executes the procedure directly without repeating the investigation.

### codebase memory
structural awareness of local file paths, function definitions, and module boundaries. verified against the filesystem using drift detection.

---

## 4. multi-channel hybrid retrieval

no single search algorithm can handle all query types. a query like *"why did we stop using rclone for Steam downloads?"* requires semantic understanding of "stop using", lexical matching for "rclone" and "Steam", and causal link traversal to find the root cause.

an unbound cognition engine executes five parallel retrieval channels for every query:

```
                         Query
                           |
       +---------+---------+---------+---------+
       |         |         |         |         |
       v         v         v         v         v
     Dense     BM25      Graph    Hopfield   Exact
     Vector   Lexical     BFS    Associative Phrase
     (HNSW)    (FTS)    (1-Hop)   (Energy)   (Literal)
       |         |         |         |         |
       +---------+---------+---------+---------+
                           |
                           v
              [ Intent-Aware RRF Fusion ]
                           |
                           v
                [ Cross-Encoder Rerank ]
                           |
                           v
             [ Temporal Gaussian Kernel ]
                           |
                           v
             [ Noise Gate / Cutoff Filter ]
                           |
                           v
                       Final Top-K
```

### channel 1: dense vector (HNSW)
approximate nearest-neighbor search across dense embedding space (e.g. 384-dimensional or 1024-dimensional vectors). to scale beyond toy datasets, engines must use hierarchical navigable small world (HNSW) graphs with $O(\log N)$ search complexity rather than brute-force $O(N)$ linear scans.

### channel 2: lexical full-text (BM25)
traditional BM25 text ranking over inverted token indexes. captures exact terms, rare words, error codes, and variable names that dense vector embeddings blur.

### channel 3: graph traversal (BFS)
extracts named entities from the query and performs a 1-hop breadth-first search across the entity relationship graph. this retrieves structurally related memories even when they share zero overlapping words with the query.

### channel 4: associative pattern completion (Hopfield)
implements a continuous modern Hopfield energy network:

$$\xi_{\text{new}} = X^T \cdot \text{softmax}(\beta \cdot X \cdot \xi)$$

where $X$ represents the stored memory matrix and $\beta$ is the inverse temperature parameter. this channel retrieves memories that belong to the same broader cognitive pattern or operational context, completing patterns from partial cues.

### channel 5: exact phrase matching
scans for quoted substrings and exact symbol matches, giving deterministic priority to literal file paths and exact code identifiers.

---

## 5. intent-aware fusion & calibrated reranking

### reciprocal rank fusion (RRF)
combining raw scores from five distinct channels fails because score distributions, scales, and variances differ radically. unbound cognition uses Reciprocal Rank Fusion:

$$RRF(d) = \sum_{c \in \text{channels}} w_c(\text{intent}) \cdot \frac{1}{k + \text{rank}_c(d)}$$

where $k \approx 60$.

crucially, the channel weights $w_c$ are not static. the engine classifies query intent and adjusts channel weights dynamically:

| Detected Query Intent | Dense Vector | BM25 Lexical | Graph BFS | Temporal | Procedural Boost |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **"how"** (procedure) | 0.8 | 1.2 | 0.6 | 0.4 | **2.0x** |
| **"who" / "what"** (entity) | 0.9 | 1.0 | **1.8** | 0.5 | 1.0x |
| **"when"** (timeline) | 0.6 | 0.8 | 0.5 | **2.5** | 0.5x |
| **"why"** (cause / decision) | **1.4** | 0.7 | 1.2 | 0.8 | 1.2x |
| **general** | 1.0 | 1.0 | 1.0 | 1.0 | 1.0x |

### cross-encoder reranking
the top 20 candidate memories from RRF pass through a cross-encoder model. unlike bi-encoders which encode query and document into separate vectors, a cross-encoder attends across all query tokens and memory tokens simultaneously via full self-attention.

the resulting raw logit $s$ is normalized using a calibrated temperature-scaled sigmoid:

$$S_{ce} = \frac{1}{1 + e^{-s / \tau}}$$

where $\tau$ is empirical temperature.

### temporal gaussian kernel
if a query contains relative temporal references (e.g. *"last week"* or *"3 days ago"*), memories whose `fact_date` falls within that target window receive a Gaussian score bonus centered on the target date:

$$B_{\text{temporal}} = \alpha \cdot \exp\left( -\frac{(t - t_{\text{target}})^2}{2\sigma^2} \right)$$

### noise & confidence threshold gating
the final score is checked against an empirical confidence threshold (default $0.35$). candidates falling below the threshold are discarded.

**a memory engine must be willing to return an empty list.** forcing low-confidence matches into an agent's context window is the primary cause of retrieval-induced hallucination.

---

## 6. lifecycle, drift detection & belief revision

retrieving information is not proof that the information is still true. a durable cognitive system must model uncertainty and change over time.

### the four lifecycle states

```
  [ New Memory ]
        |
        v
    ( ACTIVE ) <-----------------+
        |                        |
        | challenge raised       | challenge resolved
        v                        |
  ( CHALLENGED ) ----------------+
        |
        | newer truth confirmed
        v
  ( SUPERSEDED )
        |
        | explicit pruning / expiration
        v
   ( FORGOTTEN )
```

1. **active**: verified or accepted knowledge used in default retrieval.
2. **challenged**: conflicting evidence has been recorded. the memory remains retrievable, but carries a warning badge so the agent evaluates it critically.
3. **superseded**: an updated decision or fact has replaced this record. excluded from standard search unless the agent explicitly queries historical rationale.
4. **forgotten**: soft-deleted or tombstoned. retained only as an encrypted sync tombstone to prevent resurrection across peers.

### filesystem drift detection
software projects change on disk faster than documentation updates. unbound cognition engines include automated drift checking:
- parses stored file paths, function references, and tool commands.
- inspects the physical filesystem to verify whether referenced files still exist, whether line numbers match, and whether cited CLI binaries remain installed.
- produces a drift score (0–100) and marks invalid claims with error flags.

### explicit negative knowledge
hallucination often happens when an agent asks whether a tool or configuration exists, finds no matches, and invents one.

unbound cognition supports explicit negative assertions:
```json
{
  "content": "Steam library does not support running over remote FUSE/rclone mounts due to non-blocking I/O requirements.",
  "memory_type": "negative",
  "layer": "procedural"
}
```
when the agent considers attempting that action, the negative memory matches and blocks the hallucinated approach.

---

## 7. zero-knowledge multi-device replication

engineers work across multiple machines: a laptop at a cafe, a desktop workstation at home, and remote VPSes in datacenters. keeping memory synchronized across these devices without handing plaintext notes to third-party cloud vendors is a foundational requirement.

### threat model
1. **untrusted relays**: any intermediate server, S3 bucket, or sync server is assumed to be fully readable by third parties.
2. **zero-plaintext leak**: both the markdown text content and the dense floating-point vector embeddings must be encrypted before leaving localhost. if vector embeddings leak, an attacker can reconstruct approximate semantic meaning and search similarities without the original text.
3. **device autonomy**: devices must be able to operate disconnected for weeks, make local edits, and reconcile cleanly upon reconnecting.

### cryptographic envelope
every synchronization unit is an authenticated, encrypted event record conforming to `schemas/sync-envelope.schema.json`:

```json
{
  "event_id": "019dca9f-7d01-7c33-981e-722195058d50",
  "memory_id": "019dca9f-7d01-7c33-981e-722195058d48",
  "device_id": "aris-macbook-air",
  "sequence": 1420,
  "timestamp": 1790584400000,
  "operation": "upsert",
  "crypto": {
    "algorithm": "ChaCha20-Poly1305",
    "key_id": "primary",
    "nonce": "d8f92a4b1c8e034f5a6b7c8d",
    "ciphertext": "base64_encrypted_payload...",
    "tag": "base64_poly1305_tag..."
  }
}
```

- **algorithm**: 256-bit ChaCha20-Poly1305 authenticated encryption (AEAD).
- **keys**: 32-byte symmetric master key generated locally (`engram sync keygen`) and stored with 0600 permissions at `~/.config/engram/sync.key`.
- **nonces**: 96-bit cryptographically secure random nonces per envelope.

### conflict resolution & causal preservation
when multiple devices write concurrently, state is reconciled deterministically:
1. **Lamport clocks & Last-Write-Wins**: each device maintains a monotonically increasing sequence counter. simple metadata updates resolve by highest sequence and logical timestamp.
2. **tombstone propagation**: deletions emit an authenticated `tombstone` event. peers mark the memory as forgotten rather than silently deleting it, preventing deleted records from resurrecting when an offline device reconnects.
3. **fork preservation**: if two devices edit the substantive content of the same memory concurrently, the engine does not overwrite either thought. the winning Lamport edit becomes the `active` record, and the conflicting edit is preserved as an alternative observation linked by `causal_parent_id`.

---

## 8. trade-offs, limits & when not to use this

an honest engineering paper must state its costs and failure modes. unbound cognition is not the right tool for every task.

### 1. local compute & indexing latency
running 5-channel retrieval, HNSW ANN graph updates, and a cross-encoder model locally consumes compute. on Apple Silicon (M-series), full 5-channel search with reranking takes approximately 20–35 milliseconds. on low-power single-core VPSes, cross-encoder reranking can take 150–300 milliseconds. if your agent requires sub-10ms response loops, disable local cross-encoder reranking and rely on pure RRF.

### 2. disk footprint
storing SQLite WAL logs, HNSW vector graph files, inverted full-text indexes, and encrypted sync journals requires disk space. an engram database with 5,000 memories and 25,000 entity relationships consumes approximately 60–80 MB of disk space. this is negligible on a workstation, but relevant on micro-containers.

### 3. cold-start complexity
unlike calling a hosted cloud memory endpoint with an API key, running a local cognitive substrate requires a local process, a database file, and embedding weights. the companion desktop app (`engram-desktop`) and CLI daemon automate this, but it is fundamentally more machinery than a raw API call.

### 4. when a simple markdown file is better
if a project has fewer than 20 instructions and never changes, putting an `AGENTS.md` file in the repo root is simpler, faster, and requires zero software. unbound cognition is built for ongoing, multi-month workflows where knowledge evolves, context outgrows single prompts, and work spans multiple agents and machines.

---

## 9. the unbound cognition ecosystem

the open cognitive memory standard is implemented across three interoperable layers:

1. **[`spec`](https://github.com/Unbound-Cognition/spec)** — the normative protocol, data models, wire contracts, and formal JSON Schemas (`memory`, `checkpoint`, `query`, `sync-envelope`).
2. **[`engram`](https://github.com/Unbound-Cognition/engram)** — the reference Python engine providing local storage (SQLite/Postgres), the 5-channel retrieval pipeline, the zero-knowledge sync engine, the MCP server, and the web workspace.
3. **[`engram-desktop`](https://github.com/Unbound-Cognition/engram-desktop)** — the native macOS SwiftUI companion providing menu bar status, daemon supervision, one-click agent wiring for Claude/Codex/Cursor, and the global `⌘⇧M` quick recall HUD.

all code and specifications are published openly under the Unbound Cognition organization:

- **specifications:** https://github.com/Unbound-Cognition/spec
- **core engine:** https://github.com/Unbound-Cognition/engram
- **desktop app:** https://github.com/Unbound-Cognition/engram-desktop
- **organization:** https://github.com/Unbound-Cognition
