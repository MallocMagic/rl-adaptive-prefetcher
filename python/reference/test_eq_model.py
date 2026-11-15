"""Tests for eq_model.py. Run with: python3 test_eq_model.py  (or pytest)."""
import random
from eq_model import *

L = lambda i: 1000 + i            # accepted-prefetch line for event i


def build(eq, spec):
    """spec: list of (outcome, action) for events 0..n-1. State = event index."""
    for i, (o, a) in enumerate(spec):
        eq.insert(i, a, L(i), o)


def test_fewer_than_16_events():
    eq = EQ(16)
    build(eq, [(ACCEPTED, 0), (NO_PREFETCH, 0), (ACCEPTED, 0), (OUT_OF_PAGE, 0), (ACCEPTED, 0)])
    assert eq.stats["updates_in_run"] == 0 and len(eq.entries) == 5
    eq.drain()
    assert [r["r1"] for r in eq.log] == [-896, -128, -896, -768]
    assert [eq.q[(i, 0)] for i in range(4)] == [120, 126, 120, 121]
    assert (4, 0) not in eq.q                                   # last entry: no update
    assert eq.stats["discarded"] == 1 and eq.stats["unfilled_at_drain"] == 3
    assert eq.stats["updates_drain"] == 4                       # n - 1


def test_exactly_16_events():
    eq = EQ(16)
    eq.insert(0, 0, L(0), ACCEPTED)
    assert eq.fill(L(0)) and eq.match(L(0))                     # filled, then used: timely
    for i in range(1, 15):
        eq.insert(i, 0, L(i), NO_PREFETCH)
    eq.insert(15, 0, L(15), ACCEPTED)
    assert len(eq.entries) == 16 and eq.stats["updates_in_run"] == 0   # no retirement yet
    eq.drain()
    assert eq.stats["updates_drain"] == 15 and eq.stats["discarded"] == 1
    assert eq.log[0]["r1"] == 1280 and eq.q[(0, 0)] == 137
    assert all(eq.q[(i, 0)] == 126 for i in range(1, 15))
    assert (15, 0) not in eq.q


def test_17_events():
    eq = EQ(16)
    eq.insert(0, 0, L(0), ACCEPTED); eq.fill(L(0))              # filled, never used
    eq.insert(1, 0, L(1), ACCEPTED)                             # never filled, never used
    for i in range(2, 16):
        eq.insert(i, 0, L(i), NO_PREFETCH)
    assert eq.stats["updates_in_run"] == 0
    eq.insert(16, 0, L(16), NO_PREFETCH)                        # 17th event retires e0
    assert eq.stats["updates_in_run"] == 1 and eq.q[(0, 0)] == 120
    assert eq.log[0]["s1"] == 0 and eq.log[0]["s2"] == 1        # successor = next event
    assert eq.stats["unfilled_in_run"] == 0                     # e0 was filled
    assert len(eq.entries) == 16 and eq.entries[0].state == 1
    eq.drain()
    assert eq.stats["updates_drain"] == 15 and eq.stats["discarded"] == 1
    assert eq.stats["updates_in_run"] + eq.stats["updates_drain"] == 16        # n - 1
    assert eq.q[(1, 0)] == 120 and eq.stats["unfilled_at_drain"] == 1
    assert (16, 0) not in eq.q


def test_pending_accepted_prefetches_during_drain():
    eq = EQ(16)
    eq.insert(0, 0, L(0), ACCEPTED); eq.fill(L(0)); eq.match(L(0))          # timely
    eq.insert(1, 0, L(1), ACCEPTED); eq.match(L(1)); eq.fill(L(1))          # late, fill after match
    eq.insert(2, 0, L(2), ACCEPTED); eq.fill(L(2))                          # filled, never used
    eq.insert(3, 0, L(3), ACCEPTED)                                         # never filled, never used
    eq.insert(4, 0, L(4), IN_CACHE)                                         # duplicate
    eq.insert(5, 0, L(5), ACCEPTED)                                         # last, pending
    eq.drain()
    assert [r["r1"] for r in eq.log] == [1280, 768, -896, -896, -256]
    assert [eq.q[(i, 0)] for i in range(5)] == [137, 133, 120, 120, 125]
    assert (5, 0) not in eq.q and eq.stats["discarded"] == 1
    assert eq.stats["unfilled_at_drain"] == 2                               # e3 and e5


def test_match_keeps_entry_and_is_final():
    eq = EQ(16)
    eq.insert(0, 0, L(0), ACCEPTED)
    assert eq.match(L(0)) and eq.entries[0].reward == 768                   # late
    assert len(eq.entries) == 1                                             # entry stays queued
    assert not eq.match(L(0))                                               # no second reward
    assert eq.fill(L(0)) and eq.entries[0].filled and eq.entries[0].reward == 768   # fill cannot overwrite


def test_reprefetch_after_reward_and_unique_fill_match():
    eq = EQ(16)
    eq.insert(0, 0, L(0), ACCEPTED)
    assert eq.pending_line(L(0))
    eq.fill(L(0)); eq.match(L(0))                                           # e0 rewarded timely
    assert not eq.pending_line(L(0))                                        # no longer pending
    eq.insert(1, 0, L(0), ACCEPTED)                                         # same line again: allowed
    assert eq.fill(L(0)) and eq.entries[1].filled                           # fill goes to e1 only
    assert eq.match(L(0)) and eq.entries[1].reward == 1280 and eq.entries[0].reward == 1280


def test_outcome_priority():
    c = classify_outcome
    assert c(0, 100, True, True, True, True) == NO_PREFETCH
    assert c(100, 100, True, True, True, True) == OUT_OF_PAGE               # leaves the page
    assert c(1, 100, True, True, True, True) == IN_CACHE
    assert c(1, 100, False, True, True, True) == QUEUED
    assert c(1, 100, False, False, True, True) == PENDING_EQ
    assert c(1, 100, False, False, False, True) == QUEUE_FULL
    assert c(1, 100, False, False, False, False) == ACCEPTED
    assert c(-8, 3, False, False, False, False) == OUT_OF_PAGE              # negative target


def test_in_run_unfilled_retirement_is_flagged():
    eq = EQ(16)
    eq.insert(0, 0, L(0), ACCEPTED)                                         # never filled
    for i in range(1, 17):
        eq.insert(i, 0, L(i), NO_PREFETCH)
    assert eq.stats["unfilled_in_run"] == 1


def test_window_rule():
    assert window_ok(16, 8, 64) and window_ok(8, 8, 32)
    assert not window_ok(8, 8, 64)                                          # exclude from the sweep


def test_n_minus_1_updates_and_chronology():
    rng = random.Random(7)
    for n in range(0, 41):
        eq = EQ(16)
        for i in range(n):
            o = rng.choice([ACCEPTED, NO_PREFETCH, OUT_OF_PAGE, IN_CACHE, QUEUED, QUEUE_FULL, PENDING_EQ])
            eq.insert(i, 0, L(i), o)
        eq.drain()
        assert eq.stats["updates_in_run"] + eq.stats["updates_drain"] == max(n - 1, 0)
        assert [r["s1"] for r in eq.log] == list(range(max(n - 1, 0)))     # retirement = insertion order
        assert all(r["s2"] == r["s1"] + 1 for r in eq.log)                  # successor = next decision


def test_lfsr_and_exploration_mapping():
    s, seq = 0xACE1, []
    for _ in range(8):
        s = lfsr_step(s); seq.append("%04X" % s)
    assert seq == ["5670", "AB38", "559C", "2ACE", "1567", "8AB3", "4559", "22AC"]
    counts = [0] * 12
    for x in range(256):
        counts[(x * 12) >> 8] += 1
    assert set(counts) == {21, 22} and sum(counts) == 256
    assert all(((x * 16) >> 8) == x >> 4 for x in range(256))               # 16 actions: top 4 bits
    assert explore_action(0x3FC0, 12) == 11 and explore_action(0x0000, 12) == 0


def test_update_examples():
    assert sarsa_update(640, 1280, 960) == 649
    assert sarsa_update(500, -896, 130) == 489


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t(); print("ok  ", t.__name__)
    print(len(tests), "tests passed")
