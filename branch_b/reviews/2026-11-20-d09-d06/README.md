# D09 and D06 Public Development Evidence

Executed November 20, 2026 on a clean checkout of [51eca31](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/commit/51eca3158bff46bf52c04ec592c71559cb2ad637) under Python 3.14.10, NumPy 2.5.3, pytest 8.4.2 and jsonschema 4.26.0. The full regression passed **847 tests** after installing the repository-declared validation and transport dependencies.

## Fixed Four-Point Example

The [November 20 D09 proposal](../../decision_proposals/week11_pl_decision_review_2026-11-20.md) fixed the two training rows and four test rows before execution. The D06 extension uses a separate validation array with the same arithmetic values as test, one candidate, and the earlier public exercise's seed 17, eight attempts and 30-second per-fit development guard. No fitter inputs, rules, seed or attempt count were adjusted after observing results. The development fitter receives only the matrices and sample identities, while the triplet scoring routine receives the hand-written expected pairs.

- Actual train-only standardization and native Chebyshev geometry give maximum within-group distance **0.25**, minimum between-group distance **1.75** and gap **1.50**. The hand-written paired tree and star score 4/4 and 0/4, respectively.
- The actual D06 fitter reaches a nonconstant reference after **441 completed updates**. The reference tree correctly resolves **4/4** eligible triplets.
- Bootstrap attempts **3, 4, 5 and 6** give distinct-original LCA-depth stability **1.0**. Attempt 2 gives `INSUFFICIENT_BOOTSTRAP`. Attempts 0, 1 and 7 give `DEGENERATE_DISTANCE` after their two-row training draw repeats one observation.
- Both archived runs agree on every recorded value except the 19 elapsed-time fields. The first recorder invocation encountered a nested development dataclass when exporting a successful ledger. The recorder was corrected to serialize it. Both archived runs use the same corrected recorder and original experiment settings.

This supplies a successful nonconstant-reference example through the actual development entry point. The three-point example's collapsed-reference result remains part of the evidence. This four-point exercise leaves the qualifying D09 control, scientific minimum, registered failure mapping, reliability decision, production integration and pilot gates open.

## Reproduction

Install the stated package versions and use a clean, separate clone at the source commit. Run the [recorder](worked_example.py) with a fresh output path.

```bash
python worked_example.py --source-root <source-checkout> --output <new-receipt.json>
```

| Archive | SHA-256 of the compressed file |
| --- | --- |
| [First complete receipt](d09-d06-verified.json.gz) | `1a4ed75d29f5f731001ede3cbc361b24e2fab43e1edc708056ba71e39536ad20` |
| [Repeat receipt](d09-d06-repeat.json.gz) | `317265962dc00aae28e1558ed8b600c0447ac0e8d02142a68c40907641fac8af` |

## D13 Failure-Penalty Example

For a complete four-attempt ledger with successful scores 0, 1 and 1/2, and one failure, the successful mean is 1/2. Assigning the failure the proposed lower-bound score -2 produces a penalized mean of -1/8. In general the gap between the successful mean and penalized mean equals the failed-attempt fraction times the successful mean plus 2, with the latter two terms grouped together.

Exact enumeration in Python 3.14.10 gives the following illustrative nearest-rank endpoints. Each draw is an ordered resample of the corresponding ledger, of the same size as that ledger. This exercise shows the mechanical effect of changing the inferential target. The nominal method, seed namespace, calibration reference and consequences remain for statistical review.

| Ledger | Ordered resamples | Endpoint ranks | Endpoint values |
| --- | ---: | --- | --- |
| Three successful scores | 27 | 1, 27 | 0, 1 |
| Four attempts with penalty | 256 | 7, 250 | -11/8, 3/4 |

## Post-Execution Gate Check

The existing pre-pilot and minimum-effect checks returned `BLOCKED` against the PL documentation checkpoint. D10's October 20 intake records a proposed 0.05 absolute rooted-triplet accuracy difference. Closure requires original decision authority and pre-inspection chronology. D16/D17 remain deferred in the available October 20 response record and require the original questions.

Project Boundary. The source, fixture, recorder and receipts use public Branch B arithmetic and observable-side development only.
