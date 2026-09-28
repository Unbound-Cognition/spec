# 03. retrieval contract

this document specifies the multi-channel retrieval pipeline, intent-aware fusion, and reranking protocol required for state-of-the-art memory recall.

## 1. the retrieval pipeline

single-vector cosine search fails on edge cases: temporal queries ("what did we do 2 weeks ago?"), exact keywords ("error code 0x80070005"), and procedural links.

a conforming cognitive engine executes a 5-channel hybrid retrieval pipeline:

```
 Query
   |
   +---> [ 1. Dense Vector (HNSW) ] ------+
   |                                       |
   +---> [ 2. Full-Text (BM25) ] ----------+
   |                                       |
   +---> [ 3. Graph Traversal (BFS) ] ----+----> [ Intent-Aware RRF Fusion ]
   |                                       |                |
   +---> [ 4. Associative (Hopfield) ] ----+                v
   |                                       |     [ Cross-Encoder Rerank ]
   +---> [ 5. Exact Phrase Match ] --------+                |
                                                            v
                                                 [ Temporal Kernel + Gate ]
                                                            |
                                                            v
                                                       Final Top-K
```

---

## 2. the five retrieval channels

1. **dense embedding (HNSW)**:
   approximate nearest-neighbor search across dense vector space. captures high-level semantic similarity. must use HNSW or equivalent sub-linear index ($O(\log N)$) to scale beyond toy memory stores.
2. **full-text lexical (BM25)**:
   traditional term-frequency / inverse-document-frequency ranking. captures exact symbols, variable names, and technical terms that dense vector embeddings blur.
3. **graph traversal (BFS)**:
   extracts entities from the query and traverses 1-hop relationships in the entity graph. surfaces structurally related memories that share no overlapping keywords with the query.
4. **associative pattern completion (Hopfield)**:
   modern continuous Hopfield energy network:
   $$\xi_{\text{new}} = X^T \cdot \text{softmax}(\beta \cdot X \cdot \xi)$$
   retrieves memories based on composite pattern associations rather than single pairwise similarity.
5. **exact phrase matching**:
   detects quoted substrings and specific multi-word tokens. gives deterministically high rank to exact title or code snippet lookups.

---

## 3. intent-aware reciprocal rank fusion (RRF)

raw channel scores cannot be naively summed because their score distributions differ. engines must use Reciprocal Rank Fusion:

$$RRF(d) = \sum_{c \in \text{channels}} w_c(intent) \cdot \frac{1}{k + \text{rank}_c(d)}$$

where $k \approx 60$ and channel weights $w_c$ adapt dynamically based on detected query intent:

| Detected Intent | Dense Vector | BM25 Lexical | Graph BFS | Temporal | Procedural Boost |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **"how"** (procedure) | 0.8 | 1.2 | 0.6 | 0.4 | **2.0x** |
| **"who" / "what"** (entity) | 0.9 | 1.0 | **1.8** | 0.5 | 1.0x |
| **"when"** (timeline) | 0.6 | 0.8 | 0.5 | **2.5** | 0.5x |
| **"why"** (decision/cause) | **1.4** | 0.7 | 1.2 | 0.8 | 1.2x |
| **general** | 1.0 | 1.0 | 1.0 | 1.0 | 1.0x |

---

## 4. reranking & temporal calibration

the top $M$ candidates (typically $M=20$) from RRF fusion pass through a local cross-encoder model:

1. **cross-encoder score**:
   evaluates the concatenated `(query, memory_content)` text pair directly. produces a raw logit score.
2. **sigmoid calibration**:
   logits are normalized via calibrated sigmoid:
   $$S_{ce} = \frac{1}{1 + e^{-s / \tau}}$$
3. **temporal gaussian boost**:
   for queries specifying a relative time window (e.g. *"last week"* or *"3 days ago"*), target dates matching the window receive a Gaussian score bonus centered on the target date.
4. **noise & threshold gate**:
   candidates below an empirical confidence threshold (e.g. $S < 0.35$) are discarded. the engine must return an empty list rather than inject low-scoring noise that induces agent hallucinations.
