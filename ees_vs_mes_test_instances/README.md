# EES vs MES Test Instances

These 10 instances demonstrate the difference between **Exact Equal Shares (EES)** and **Method of Equal Shares (MES/Waterflow)**.

## Key Difference

- **EES**: All paying voters contribute **exactly equal** amounts
- **MES**: Poor voters can contribute **less than equal share** (their entire remaining budget)

## Quick Results Summary

| Instance | Budget | EES Result | MES Result | Differs? |
|----------|--------|------------|------------|----------|
| 01 | 40 (10/voter) | {A, B} cost=20 | {A, B, C} cost=40 | ✓ Winners |
| 02 | 24 (8/voter) | {B} cost=12 | {B} cost=12 | ✗ Same |
| 03 | 24 (8/voter) | {A} cost=8 | {A, B} cost=22 | ✓ Winners |
| 04 | 40 (10/voter) | {C} cost=15 | {A, C} cost=30 | ✓ Winners |
| 05 | 21 (7/voter) | {A, B} cost=17 | {A, B} cost=17 | ✗ Same |
| 06 | 36 (9/voter) | {B, C} cost=26 | {B, C} cost=26 | ✗ Same |
| 07 | 40 (10/voter) | {B} cost=10 | {B, C} cost=25 | ✓ Winners |
| 08 | 32 (8/voter) | {A, B} cost=26 | {A, B} cost=26 | ✗ Same |
| 09 | 36 (9/voter) | {B, C} cost=18 | {A, B, C} cost=36 | ✓ Winners |
| 10 | 50 (10/voter) | {B, C} cost=35 | {B, C} cost=35 | ✓ Payments |

**6/10 instances differ** (5 with different winners, 1 with different payments)

---

## Manual Verification Guide

### Instance 01: Basic Difference

**Setup:**
- Budget: 40 (4 voters × 10 each)
- Project A: cost=10, supporters={0, 1}
- Project B: cost=10, supporters={1, 2}
- Project C: cost=20, supporters={0, 2, 3}

**Approvals:**
- Voter 0: {A, C}
- Voter 1: {A, B}
- Voter 2: {B, C}
- Voter 3: {C}

**EES Execution:**
1. Compare BpB: A=2/10=0.2, B=2/10=0.2, C=3/20=0.15
2. A and B tie, B wins (larger ID)
3. B: voters 1,2 each pay 5. Leftover: v0=10, v1=5, v2=5, v3=10
4. A: voters 0,1 each pay 5. Leftover: v0=5, v1=0, v2=5, v3=10
5. C: needs 20/3≈6.67/voter. v1 has 0, can't afford → C fails
6. **EES selects: {A, B}**

**MES Execution:**
1-4. Same as EES, select A and B
5. C: v0 has 5, v2 has 5, v3 has 10
   - v0 pays 5 (all they have)
   - v2 pays 5 (all they have)
   - v3 pays 10 (the rest)
   - Total: 5+5+10=20 ✓
6. **MES selects: {A, B, C}**

---

### Instance 03: Cascading Poverty

**Setup:**
- Budget: 24 (3 voters × 8 each)
- Project A: cost=8, supporters={0, 1}
- Project B: cost=14, supporters={0, 1, 2}

**Approvals:**
- Voter 0: {A, B}
- Voter 1: {A, B}
- Voter 2: {B}

**EES Execution:**
1. BpB: A=2/8=0.25, B=3/14≈0.21
2. A wins: v0,v1 each pay 4. Leftover: v0=4, v1=4, v2=8
3. B: needs 14/3≈4.67/voter. v0,v1 have only 4 each → fails
4. **EES selects: {A}**

**MES Execution:**
1-2. Same, select A
3. B: v0 has 4, v1 has 4, v2 has 8
   - v0 pays 4 (all)
   - v1 pays 4 (all)
   - v2 pays 6 (remaining 14-4-4=6)
   - Total: 4+4+6=14 ✓
4. **MES selects: {A, B}**

---

### Instance 07: Rich Poor Divide

**Setup:**
- Budget: 40 (4 voters × 10 each)
- Project A: cost=20, supporters={0, 1}
- Project B: cost=10, supporters={0, 2, 3}
- Project C: cost=15, supporters={1, 3}

**Approvals:**
- Voter 0: {A, B}
- Voter 1: {A, C}
- Voter 2: {B}
- Voter 3: {B, C}

**EES Execution:**
1. BpB: A=2/20=0.1, B=3/10=0.3, C=2/15≈0.13
2. B wins: v0,v2,v3 each pay 10/3≈3.33
3. Leftover: v0≈6.67, v1=10, v2≈6.67, v3≈6.67
4. C: needs 15/2=7.5/voter. v3 has only 6.67 → fails
5. **EES selects: {B}**

**MES Execution:**
1-3. Same, select B
4. C: v1 has 10, v3 has 6.67
   - v3 pays 6.67 (all)
   - v1 pays 8.33 (remaining 15-6.67=8.33)
   - Total: 6.67+8.33=15 ✓
5. **MES selects: {B, C}**

---

### Instance 09: Asymmetric Costs

**Setup:**
- Budget: 36 (4 voters × 9 each)
- Project A: cost=18, supporters={0, 1, 2}
- Project B: cost=12, supporters={0, 3}
- Project C: cost=6, supporters={1, 3}

**Approvals:**
- Voter 0: {A, B}
- Voter 1: {A, C}
- Voter 2: {A}
- Voter 3: {B, C}

**EES Execution:**
1. BpB: A=3/18≈0.17, B=2/12≈0.17, C=2/6≈0.33
2. C wins: v1,v3 each pay 3. Leftover: v0=9, v1=6, v2=9, v3=6
3. BpB: A=3/18≈0.17, B=2/12≈0.17. B wins (larger ID)
4. B: v0,v3 each pay 6. Leftover: v0=3, v1=6, v2=9, v3=0
5. A: needs 18/3=6/voter. v0 has 3 → fails
6. **EES selects: {B, C}**

**MES Execution:**
1-4. Same, select C and B
5. A: v0 has 3, v1 has 6, v2 has 9
   - v0 pays 3 (all)
   - v1 pays 6 (all)
   - v2 pays 9 (remaining 18-3-6=9)
   - Total: 3+6+9=18 ✓
6. **MES selects: {A, B, C}**

---

## File Format

Each `.pb` file uses the Pabulib format:
```
META
key;value
budget;X
...
PROJECTS
project_id;name;cost;votes
A;Project A;10;2
...
VOTES
voter_id;vote
1;A,B
2;A
...
```

