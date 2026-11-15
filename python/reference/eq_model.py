"""
Reference model of the Evaluation Queue (EQ), outcome rules and SARSA update.
Spec v0.1 (Person 2). Integer arithmetic only, so it can be compared with the RTL.

Rewards are raw values (reward x 64, 6 fractional bits).
"""
from collections import deque

FRAC = 6
Q0 = 2 << FRAC                                   # initial Q = 2.0 -> raw 128
REWARD = {"AT": 20, "AL": 12, "CL": -12, "IN": -14, "NP": -2, "DUP": -4, "QF": -2}
RAW = {k: v * (1 << FRAC) for k, v in REWARD.items()}

# Outcome codes (3 bits)
ACCEPTED, NO_PREFETCH, OUT_OF_PAGE, IN_CACHE, QUEUED, QUEUE_FULL, PENDING_EQ = 0, 1, 2, 3, 4, 5, 6
IMMEDIATE = {NO_PREFETCH: "NP", OUT_OF_PAGE: "CL", IN_CACHE: "DUP",
             QUEUED: "DUP", QUEUE_FULL: "QF", PENDING_EQ: "DUP"}


def sarsa_update(q1, r, q2):
    g = (9 * q2) >> 4            # gamma = 9/16, arithmetic shift = floor
    target = r + g
    err = target - q1
    delta = err >> 7             # alpha = 1/128, floor
    return max(-32767, min(32767, q1 + delta))


def classify_outcome(offset, demand_line, in_cache, queued_or_inflight, pending_in_eq, queue_full):
    """Priority order is part of the spec: the first matching rule wins."""
    if offset == 0:
        return NO_PREFETCH
    target = demand_line + offset
    if target < 0 or (target >> 6) != (demand_line >> 6):
        return OUT_OF_PAGE
    if in_cache:
        return IN_CACHE
    if queued_or_inflight:
        return QUEUED
    if pending_in_eq:
        return PENDING_EQ
    if queue_full:
        return QUEUE_FULL
    return ACCEPTED


def lfsr_step(s):
    bit = ((s >> 0) ^ (s >> 2) ^ (s >> 3) ^ (s >> 5)) & 1
    return (s >> 1) | (bit << 15)


def explore_test(lfsr):
    return (lfsr & 0x3F) == 0                    # epsilon = 1/64


def explore_action(lfsr, num_actions):
    r8 = (lfsr >> 6) & 0xFF
    return (r8 * num_actions) >> 8               # scaled mapping, no modulo


def window_ok(eq_depth, spacing, latency, margin=2):
    """An accepted prefetch must be filled before its EQ entry retires during a run."""
    return eq_depth * spacing > latency + margin


class Entry:
    __slots__ = ("state", "action", "line", "outcome", "filled", "reward")

    def __init__(self, state, action, line, outcome, reward):
        self.state, self.action, self.line = state, action, line
        self.outcome, self.filled, self.reward = outcome, False, reward


class EQ:
    def __init__(self, depth=16, q=None):
        assert depth >= 2
        self.depth = depth
        self.entries = deque()
        self.q = {} if q is None else q
        self.log = []
        self.stats = dict(updates_in_run=0, updates_drain=0, discarded=0,
                          unfilled_in_run=0, unfilled_at_drain=0)

    def qget(self, s, a):
        return self.q.get((s, a), Q0)

    def pending_line(self, line):
        return any(e.outcome == ACCEPTED and e.reward is None and e.line == line
                   for e in self.entries)

    def insert(self, state, action, line, outcome):
        reward = None if outcome == ACCEPTED else RAW[IMMEDIATE[outcome]]
        if len(self.entries) == self.depth:
            self._retire(in_run=True)
        self.entries.append(Entry(state, action, line, outcome, reward))

    def match(self, line):
        """A demand assigns a reward to the oldest pending entry; the entry stays queued."""
        for e in self.entries:
            if e.outcome == ACCEPTED and e.reward is None and e.line == line:
                e.reward = RAW["AT"] if e.filled else RAW["AL"]
                return True
        return False

    def fill(self, line):
        """A fill sets the filled bit only. It never changes a reward."""
        for e in self.entries:
            if e.outcome == ACCEPTED and e.line == line and not e.filled:
                e.filled = True
                return True
        return False

    def _retire(self, in_run):
        head = self.entries.popleft()
        if head.reward is None:
            head.reward = RAW["IN"]
            if not head.filled:
                self.stats["unfilled_in_run" if in_run else "unfilled_at_drain"] += 1
        if not self.entries:                                  # last entry: no successor
            self.stats["discarded"] += 1
            return None
        nxt = self.entries[0]
        q1, q2 = self.qget(head.state, head.action), self.qget(nxt.state, nxt.action)
        new = sarsa_update(q1, head.reward, q2)
        self.q[(head.state, head.action)] = new
        self.stats["updates_drain" if not in_run else "updates_in_run"] += 1
        row = dict(s1=head.state, a1=head.action, r1=head.reward,
                   s2=nxt.state, a2=nxt.action, q1_old=q1, q1_new=new, drain=not in_run)
        self.log.append(row)
        return row

    def drain(self):
        while self.entries:
            self._retire(in_run=False)
