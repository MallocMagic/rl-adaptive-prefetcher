# Cache Specification Draft

**Status:** DRAFT — NOT APPROVED FOR RTL IMPLEMENTATION

## 1. Purpose

Define the behavior and interfaces of the simplified cache/memory subsystem
used to evaluate no-prefetch, stride-prefetch, and RL-prefetch modes.

This document is a working proposal. Changes require review by the team.

## 2. Existing Project Conventions

The current project context specifies:

- Cache-line size: 64 bytes.
- Page size: 4 KiB.
- Addressing: byte-addressed, with zero-based indexing.
- Prefetch addresses must remain within the current 4 KiB page.

Confirm these conventions with the team before treating this draft as the
final interface contract.

## 3. Provisional Cache Configuration

| Parameter | Proposed value | Status |
|---|---|---|
| Data capacity | 4 KiB | Provisional |
| Associativity | 2-way | Provisional |
| Line size | 64 bytes | Existing convention; confirm |
| Number of sets | 32 | Derived from the proposed capacity and associativity |
| Replacement policy | LRU | Provisional |
| Outstanding demand misses | 1 | Provisional |
| Prefetch queue depth | 2 requests | Provisional |
| Memory response latency | Fixed | Exact cycle count unresolved |
| Cache write policy | Unresolved | Team decision required |
| Write allocation policy | Unresolved | Team decision required |

For the proposed 4 KiB cache:

sets = capacity / (line size × associativity)
     = 4096 / (64 × 2)
     = 32 sets

The 32-set result is valid only if the proposed 4 KiB capacity, 64-byte line,
and 2-way associativity are all retained.

## 4. Required Behavioral Decisions

### Demand path
- Request and response handshake.
- Read and write request semantics.
- Behavior when a request is presented while the cache is busy.
- Whether requests may be backpressured.
- Reset behavior and initial cache validity.
- Whether one or multiple demand misses may be outstanding.

### Memory model
- Request acceptance and response timing.
- Whether memory requests can be stalled.
- Read and write response behavior.
- Ordering guarantees.
- End-of-trace behavior.

### Prefetch path
- How a prefetch request is accepted or rejected.
- Demand priority when demand and prefetch requests compete.
- Duplicate detection against cache lines, outstanding misses, and queued requests.
- Queue-full behavior.
- Invalid, unaligned, or out-of-page request handling.
- Whether a demand request can promote or merge with an outstanding prefetch.
- How prefetches are cancelled, dropped, or drained.

### Fill tracking and metadata
- How demand fills are distinguished from prefetch fills.
- How a prefetched line is marked and when that mark is cleared.
- How useful prefetches are attributed to their originating request.
- How unused prefetched-line evictions are counted.
- Whether transaction IDs are required.

### Replacement and pollution
- Exact LRU update rules.
- How demand hits, demand fills, and prefetch fills affect replacement state.
- Whether prefetch fills may evict demand-fetched lines.
- How pollution and unused prefetches are measured.

### RL integration
- State and action encodings.
- Prefetcher request/response contract.
- Reward event definitions and timing.
- Ownership of the Evaluation Queue and reward/update logic.
- Association between an action, its prefetch request, the resulting fill,
  and delayed reward feedback.
- Fixed-point Q-value format, rounding, saturation, and update order.
- Reset behavior, deterministic tie-breaking, and exploration sequence.

## 5. Candidate Address Breakdown

With 64-byte lines and 4 KiB pages:
- Byte offset within a cache line: 6 bits.
- Offset within a 4 KiB page: 12 bits.
- Line number within a page: 64 lines.

For a 32-set cache, the set index uses 5 bits. The tag width depends on the
system address width and the final cache organization.

Confirm the address width and address representation used by the trace format.

## 6. Verification Requirements

Before integration, tests should cover:
- Reset and initial state.
- Demand hit and miss.
- Replacement and eviction.
- Backpressure and busy behavior.
- Demand/prefetch contention.
- Duplicate and out-of-page prefetch requests.
- Queue full and empty conditions.
- Prefetch fill attribution and usefulness tracking.
- Simultaneous events and delayed reward association.
- Trace termination and drain behavior.

Python reference behavior and RTL behavior must be compared using identical
inputs, event ordering, and documented timing assumptions.

## 7. Approval Gate

Do not treat this document as the final specification until the team agrees on:
- Cache parameters.
- Request/response timing.
- Write policy.
- Miss concurrency.
- Prefetch queue and duplicate behavior.
- Fill tracking and metric definitions.
- RL/reward interface ownership.
- Module boundaries and integration schedule.

Record approved changes in the team decision log and update this draft.
