# 01. core architecture

this document outlines the cognitive layers, lifecycle stages, and threat model for sovereign agent memory.

## 1. cognitive layers

memory is not a single uniform list of vectors. human cognition separates what you are thinking about right now, what happened this morning, general knowledge of the world, and muscle-memory procedures.

conforming systems must separate stored material into distinct layers:

### working (L0)
- **purpose**: scratchpad for active problem solving.
- **scope**: current turn or immediate session.
- **retention**: ephemeral; discarded or consolidated into higher layers upon session end.

### episodic (L1)
- **purpose**: timestamped history of what occurred.
- **scope**: chronological logs, session diaries, conversation transcripts, and event sequences.
- **retention**: decays over time based on recency and confirmation, but preserved for auditability.

### semantic (L2)
- **purpose**: stabilized world knowledge and entity relations.
- **scope**: facts about people, projects, technologies, and environments extracted from experience.
- **retention**: high stability; updated when contradicted or enriched.

### procedural (L3)
- **purpose**: reusable instructions, error resolutions, and operating patterns.
- **scope**: "when X fails with error Y, do Z", deployment steps, architectural decisions with rationale.
- **retention**: highest stability; prioritized when an agent attempts a task.

### codebase
- **purpose**: structural and architectural knowledge about specific repositories.
- **scope**: load-bearing files, symbol maps, conventions, and test setups.

---

## 2. memory types

within each layer, a memory record must declare one of four distinct functional types:

1. **fact**: a discrete assertion about reality (e.g. *"cute-vps runs Ubuntu 24.04 on IP 15.135.202.14"*).
2. **procedure**: step-by-step operational instructions or error prevention guidelines (e.g. *"when configuring libraryfolders.vdf, do not mount cloud FUSE drives under Steam"*).
3. **narrative**: a contextual account of an event or session (e.g. *"session summary of DNS migration on Sept 28"*).
4. **negative**: an explicit assertion of non-existence (e.g. *"there is no public REST endpoint for creating GitHub organizations"*). this prevents models from hallucinating non-existent tools or patterns.

---

## 3. cognitive lifecycle

memories are dynamic. a memory system that only appends new records will eventually choke on contradictions, dead links, and stale state.

conforming implementations must support the following lifecycle states:

```
[ Ingest / Extract ]
         |
         v
    ( active ) <--------+
      |      |          |
      |      +-----> ( challenged )
      |                 |
      v                 v
 ( superseded )    ( forgotten )
```

- **active**: verified and currently eligible for primary retrieval.
- **challenged**: flagged by drift detection (e.g. a referenced file no longer exists) or contradicted by a newer observation. excluded from high-confidence prompt injections until re-verified.
- **superseded**: replaced by an updated version that absorbed its context. retained for history but down-weighted in normal queries.
- **forgotten**: soft-deleted or permanently purged by explicit user request or privacy policy.

### drift detection
conforming systems should periodically verify memories referencing filesystem paths, URLs, or external entities against current reality. when an entity disappears, the memory transitions from `active` to `challenged`.

---

## 4. threat model

the architecture addresses four primary threats:

1. **vendor enclosure & amnesia**: if your agent's memory is stored inside a proprietary cloud, switching providers or getting rate-limited wipes your context. memory must be decoupled from the inference model.
2. **cognitive surveillance**: chat transcripts and memory stores contain intimate personal and operational details. raw records and vector embeddings must never be transmitted unencrypted over third-party sync relays.
3. **memory pollution / injection**: untrusted documents or adversarial prompts can attempt to inject false procedural instructions into long-term memory. writes must be gated by origin attribution, confidence checks, and user transparency.
4. **hallucinated continuity**: agents often claim to remember things they do not know. the retrieval system must distinguish between an explicit recalled record, a negative record, and an empty query result.
