"""
Exhaustive (non-random) brute-force verification for uniform utilities.

We validate Theorem 5.7 / Algorithm 5 from the paper:
    Algorithm 5 returns the minimum budget b* > b such that
        EES(E(b*)) != (W, X)
for uniform utilities (we test cost utility u(p)=cost(p)).

Strategy:
- Fix n=3, m=3, integer costs, integer budget b.
- Enumerate ALL approval profiles (2^(n*m) = 512).
- Filter to profiles where every project has at least one supporter (paper assumes WLOG).
- For each profile:
    1) Compute (W,X) = EES(E(b); cost)
    2) Compute d_alg = ADD-OPT (Algorithm 5) output.
    3) Brute-force the smallest d on a rational grid that is guaranteed to
       include the true breakpoint (denominator divides lcm(1..n) for integer costs).
    4) Assert d_alg equals the brute-force minimum d.

This is intentionally exhaustive (no sampling).
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import gcd
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scalable_proportional_pb.types import Election, Project
from scalable_proportional_pb.ees import ees_with_outcome, cost_utility
from scalable_proportional_pb.add_opt_uniform import add_opt_uniform


def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


def lcm_1_to_n(n: int) -> int:
    out = 1
    for k in range(1, n + 1):
        out = lcm(out, k)
    return out


def make_election(project_ids: list[str], costs: list[int], approvals: dict[int, set[str]], budget: int) -> Election:
    projects = {pid: Project(id=pid, cost=Fraction(c)) for pid, c in zip(project_ids, costs)}
    voters = sorted(approvals.keys())
    return Election(projects=projects, voters=voters, approvals=approvals, budget=Fraction(budget))


def outcome_differs(o1, o2) -> bool:
    # Paper treats outcome difference as either different winning set W, or different funding/payments X.
    return (o1.selected != o2.selected) or (o1.payments != o2.payments)


@pytest.mark.parametrize(
    "budget,costs",
    [
        (5, [2, 3, 4]),
        (6, [2, 3, 4]),
    ],
)
def test_add_opt_uniform_matches_bruteforce_exhaustive_n3_m3_costutility(budget: int, costs: list[int]):
    """
    Exhaustively validate Algorithm 5 (uniform utilities) on n=3,m=3.

    We test cost utility u(p)=cost(p), which is a uniform utility class considered in the paper.
    """
    project_ids = ["a", "b", "c"]
    n = 3
    m = 3

    denom = lcm_1_to_n(n)  # for n=3, denom=6
    step = Fraction(1, denom)

    # Upper bound for brute force search (per-voter increase):
    # In the worst case, you might need to raise budget to cover all costs.
    # With tiny costs this is small; we set a safe bound.
    max_total_cost = sum(costs)
    # Ensure at least enough to reach sum(costs) even if starting budget is 0:
    max_d = Fraction(max_total_cost + 5, 1)
    max_k = int(max_d / step)
    assert max_k > 0

    # Enumerate ALL approval profiles (bitmask per voter)
    # For each voter: 2^m possible approval sets.
    masks = list(range(1 << m))
    profiles_checked = 0

    for voter_masks in product(masks, repeat=n):
        approvals: dict[int, set[str]] = {}
        for v, mask in enumerate(voter_masks):
            approved = {project_ids[j] for j in range(m) if (mask >> j) & 1}
            approvals[v] = approved

        # Filter: each project must be approved by at least one voter (paper WLOG)
        if not all(any(pid in approvals[v] for v in range(n)) for pid in project_ids):
            continue

        election = make_election(project_ids, costs, approvals, budget)

        # Compute base outcome
        base_outcome = ees_with_outcome(election, cost_utility)

        # If all projects selected already, Algorithm 5 should return infinity (None); skip.
        if len(base_outcome.selected) == m:
            d_alg = add_opt_uniform(election, base_outcome, cost_utility)
            assert d_alg is None
            continue

        d_alg = add_opt_uniform(election, base_outcome, cost_utility)
        assert d_alg is not None, "With supporters for all projects, outcome must change for some increased budget"
        assert d_alg > 0

        # Brute-force smallest d on the guaranteed rational grid
        brute_d = None
        for k in range(1, max_k + 1):
            d = k * step
            new_budget = election.budget + election.n * d
            e2 = election.with_budget(new_budget)
            out2 = ees_with_outcome(e2, cost_utility)
            if outcome_differs(base_outcome, out2):
                brute_d = d
                break

        assert brute_d is not None, "Expected to find a budget where the outcome changes"
        assert brute_d == d_alg, (
            f"Algorithm 5 mismatch: d_alg={d_alg}, brute_d={brute_d}, "
            f"budget={budget}, costs={costs}, approvals={approvals}"
        )

        # Minimality check: one step smaller should not change the outcome
        if brute_d > step:
            prev_budget = election.budget + election.n * (brute_d - step)
            e_prev = election.with_budget(prev_budget)
            out_prev = ees_with_outcome(e_prev, cost_utility)
            assert not outcome_differs(base_outcome, out_prev)

        profiles_checked += 1

    # Sanity: ensure we actually checked a non-trivial number of profiles
    assert profiles_checked > 0


