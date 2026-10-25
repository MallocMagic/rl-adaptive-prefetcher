# Project Status

## Project

**Title:** RL-Based Adaptive Prefetcher for Edge Medical-Imaging AI Inference

**Stage:** Pre-development / Milestone 0

**Primary objective:** Develop and evaluate a lightweight hardware prefetcher using online tabular SARSA reinforcement learning against a no-prefetch baseline and a stride-prefetching baseline.

## Current Environment

- OS: Fedora Linux 44
- Python: 3.14.8
- Git: 2.56.0
- Verilator: 5.046
- Icarus Verilog: 13.0
- GNU Make: 4.4.1
- G++: 16.2.1
- Vivado: Not currently detected in PATH
- Repository: Local repository; no remote configured or required yet

Tool versions describe the environment at the time this file was written.
Recheck them if the environment changes.

## Scope Boundaries

The initial system is a simplified cache/memory model driven by documented
or generated CNN-style inference memory-access traces.

The project does not currently claim to implement or evaluate a complete CPU,
GPU, SoC, coherent multicore system, or full medical-imaging inference pipeline.

Potential metrics include:
- Cache miss rate
- Prefetch accuracy and coverage
- Prefetch timeliness
- Modeled stall cycles or AMAT under documented assumptions
- Unused prefetched-line evictions and cache pollution
- RTL resource use and timing, if a supported synthesis flow is available

Modeled cache metrics must not be presented as proof of end-to-end inference
speedup or energy savings.

## Team Roles

- Person 1: Trace generation, Python baseline simulator, stride baseline,
  experiments, comparison scripts, and report contributions.
- Person 2: RL state/action/reward specification, Python SARSA reference,
  RL simulator mode, Q-table/action-selection logic, SARSA RTL, and tests.
- Person 3: Cache subsystem, prefetch datapath and integration, fill tracking,
  verification, and integrated hardware evaluation.

These roles and the boundaries between modules must be confirmed by the team.

## Current Milestone

Milestone 0: Environment and interface-contract preparation.

Completed:
- Python and Git available.
- Verilator and Icarus Verilog installed and version-checked.
- GNU Make and G++ installed and version-checked.
- Local Git repository initialized on branch `main`.
- Initial directory structure created.

Not yet completed:
- Initial documentation committed.
- Cache/memory interface contract approved.
- Cache parameters and memory timing approved.
- RL and reward/update interfaces approved.
- Team ownership and schedule conflicts resolved.
- Vivado availability and target-device compatibility confirmed.

## Next Actions

1. Record initial project documentation.
2. Review open decisions with the team and supervisors.
3. Approve a versioned cache/interface contract.
4. Create small RTL and Python milestones only after the required interfaces
   and behavioral assumptions have been agreed.
