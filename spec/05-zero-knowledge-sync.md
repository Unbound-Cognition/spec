# 05. zero-knowledge sync

this document specifies the multi-device replication protocol, encryption envelope, and conflict resolution rules for keeping sovereign memory synchronized across personal hardware.

## 1. core principles

1. **untrusted relays**: any server, relay, or cloud bucket passing memory data between devices is treated as potentially compromised.
2. **zero-plaintext leak**: both the markdown text content and the dense embedding vectors must be encrypted before leaving the local device.
3. **device autonomy**: devices can operate completely offline for weeks and reconcile state cleanly upon reconnection.

---

## 2. the encrypted sync envelope

every synchronization unit is an authenticated, encrypted event record:

```json
{
  "event_id": "019dca9f-7d01-7c33-981e-722195058d50",
  "memory_id": "019dca9f-7d01-7c33-981e-722195058d48",
  "device_id": "aris-macbook-air-m5",
  "sequence": 1420,
  "timestamp": 1790584400000,
  "operation": "upsert",
  "crypto": {
    "algorithm": "ChaCha20-Poly1305",
    "key_id": "key-2026-primary",
    "nonce": "d8f92a4b1c8e034f5a6b7c8d",
    "ciphertext": "base64_encrypted_payload_containing_content_metadata_and_vectors...",
    "tag": "base64_auth_tag..."
  }
}
```

### decrypted payload structure
once decrypted by an authorized peer holding the private key, the payload yields the full memory envelope and its dense vector float arrays for local index insertion.

---

## 3. conflict resolution & CRDTs

synchronizing memory across multiple devices running local agents concurrently requires deterministic reconciliation without data loss:

1. **last-write-wins (LWW) by Lamport clock**:
   each event carries a monotonically increasing sequence number and logical timestamp.
2. **tombstone deletion**:
   deletions emit an explicit `delete` event record. physical deletion occurs only after all known peers acknowledge the tombstone, preventing deleted memories from "resurrecting" upon reconnect.
3. **fork preservation**:
   if two devices simultaneously edit the same memory with conflicting substantive content, the engine promotes one as the `active` record and attaches the second as an `alternative` observation linked by `causal_parent_id`. no human thought is discarded silently.

---

## 4. transport topologies

conforming engines support two sync topologies:

### A. direct peer-to-peer (tailnet / local network)
- devices discover each other over local network or Tailscale mesh.
- mutual TLS (mTLS) or WireGuard transport.
- direct SQLite WAL streaming or streaming NDJSON delta exchanges.

### B. untrusted relay (S3 / WebDAV)
- for devices that are not online simultaneously (e.g. laptop asleep while VPS runs).
- encrypted events are appended to a remote content-addressed storage bucket.
- the relay only sees opaque encrypted blobs and SHA-256 event hashes.
