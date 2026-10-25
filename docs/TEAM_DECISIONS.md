# Team Decisions and Open Questions

**Status:** Initial decision log  
**Rule:** An item is not approved merely because a proposed answer appears here.

## Decision Log

| ID | Question | Proposed owner(s) | Status |
|---|---|---|---|
| D01 | Confirm cache capacity, associativity, line size, and replacement policy. | All; Person 3 coordinates | Open |
| D02 | Define cache read/write behavior and write policy. | Person 3; team review | Open |
| D03 | Define demand request/response handshake and backpressure. | Person 3; team review | Open |
| D04 | Fix memory latency, request acceptance, and response ordering. | Person 3; team review | Open |
| D05 | Confirm maximum outstanding demand misses. | Person 3; team review | Open |
| D06 | Define prefetch queue-full, duplicate, and demand-priority behavior. | Person 3; Person 2 review | Open |
| D07 | Define fill metadata, prefetch usefulness, and unused-eviction accounting. | Person 3; Person 2 review | Open |
| D08 | Agree on state/action/reward encodings and the RL module interface. | Person 2; Person 3 review | Open |
| D09 | Decide who owns the Evaluation Queue and reward/update datapath. | Person 2 and Person 3 | Open |
| D10 | Resolve the stride RTL delivery deadline and fallback ownership. | Person 1, Person 3, team | Open |
| D11 | Resolve the cache-specification deadline conflict. | All | Open |
| D12 | Define the trace format and address-width assumptions. | Person 1; team review | Open |
| D13 | Confirm target FPGA, legitimate Vivado access, and evaluation plan. | All; supervisor input if needed | Open |
| D14 | Validate the claimed research contribution against prior work. | All; supervisor input | Open |

## Schedule Conflicts to Resolve

### Stride baseline

The current team plan places the Person 3 fallback takeover of stride RTL at
Week 10 if Person 1 has not delivered it. The Person 3 weekly plan expects
stride integration by Week 8.

The team must agree whether:
- Person 1 owns delivery by Week 8, with Person 3 responsible for integration;
- Person 3 takes over implementation at an earlier agreed trigger; or
- the schedule is revised.

Do not silently transfer implementation ownership.

### Cache specification

One plan places cache specification work in Week 3, while the Person 3 plan
starts cache-contract work in Week 1. Agree on a single milestone and
distinguish an initial draft from an approved specification.

## Research Novelty

The use of reinforcement learning, SARSA, FPGA RTL, or CNN-style traces alone
does not establish novelty. Prior work, including Pythia, must be examined.

The team should identify a specific, testable contribution and support it
with a literature review and reproducible measurements. Do not claim novelty
or superiority before the evidence supports it.

## Decision Record Template

For each resolved item, record:

- ID:
- Decision:
- Alternatives considered:
- Reason:
- Owner:
- Approvers:
- Date:
- Documents or modules affected:
- Verification required:

## Meeting Rule

Keep unresolved questions visible. Record the final agreement, not merely
the first suggestion. Update the specification and tests whenever an approved
decision changes observable behavior.
