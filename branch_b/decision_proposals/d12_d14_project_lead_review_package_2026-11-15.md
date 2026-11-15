# D12–D14 Branch B technical evidence and Project Lead decision package

**Prepared November 15, 2026. Status:** Handoff for Project Lead/statistical review; **not** an authorized freeze, pilot exit, numerical-setting selection, production activation, or request to inspect restricted Branch A information. All study results described here are synthetic development results, and test-pass claims are **team-reported** rather than independently authenticated from original JUnit and machine provenance.

## 1. Decision summary

| Decision | Branch B team-approved proposal / currently documented direction | Unresolved for scientific operation |
| --- | --- | --- |
| D12 | Fixed attempted-bootstrap budget, complete record of every failure, minimum successful fits, minimum distinct common observations, maximum failure fraction; failure of a reliability gate yields **indeterminate** | **Numeric** `B_min`, `n_min`, `f_max`; precise common-original-identity counting scope and failure/sensitivity convention; applicable authorized pilot-dependent freeze |
| D13 | `Q_b=S_b-min(D_b,1)`; primary mean over successful fits; **10,000** secondary resamples of successful scores (size `B_success`) to produce resampled means; nominal two-sided 95% nearest-rank endpoints 250/9750; proposed **conditional Monte Carlo** uncertainty interpretation | Statistical acceptance of target and conditional-iid assumptions, handling finite-sample undercoverage; D12/D14 integration; Project Lead protocol conformity and post-pilot freeze |
| D14 | Team has approved a proposed operational direction, historically described as Branch B-owned **master seed 36**, **500** attempted bootstrap replicates, and a timeout tied to **2× golden-case runtime** with input-size adjustment | Whether those exact numeric proposals are approved at the applicable gate; deterministic *namespaced* seed derivation, independent tier streams, timeout source/reference hardware/timing scope/size scaling, attempt precision/resources, evidence and formal freeze |

Historical D14 intake language is not an executable derivation or scaling formula. The current `run_full_pipeline_bootstrap` engine employs NumPy `SeedSequence(base_seed).spawn(n_replicates)`, sequential split draws, and an evaluator seed. Development replay tests assess **that existing implementation only**; they do not approve it as the final D14 production contract.

## 2. Development evidence, not independent certification

The team reported under an actual local Python 3.14 environment:

- D13 initial focused tests **25 passed**, initial full regression **814 passed**.
- Prespecified independent-score synthetic coverage study **2,400/2,400 trials complete**; all 6 cells completed. Underlying study journal/manifest retained locally.
- Synthetic selection/dependence study **600/600 trials complete**; full regression at that point **825 passed**.
- D13 read-only evidence-integrity audits and subsequent full regression **all passing** (exact latest JUnit totals/checksums not supplied).
- D12 fixed-attempt ledger audit, failure-preservation/index checks, and D14 development-seed replay tests plus full regression **all passing** (exact latest JUnit totals/checksums not supplied).

**Outstanding verification:** Inspect local Python 3.14 version, dependency freeze, Git HEAD and working tree, original JUnit/XML, both study manifests/journals and audit results, file SHA-256 records, and test failure/retry history. Do not upload or publish unreviewed machine-local evidence; all public-repo writes require independent Branch B permission and public-disclosure checks.

## 3. Statistical evidence D13 requires the reviewer to confront

Across the 6 cells of the 2,400-trial independent-score experiment:

| Synthetic score distribution | n=24 coverage | n=100 coverage |
| --- | ---: | ---: |
| Uniform symmetric | 374/400 = 93.5% | 386/400 = 96.5% |
| Two point | 384/400 = 96.0% | 383/400 = 95.75% |
| Skewed beta | **368/400 = 92.0%** | 380/400 = 95.0% |

The 24-success skewed-beta cell showed possible finite-sample undercoverage (user-provided 95% Wilson 88.92%–94.28%). Do not hide or retune this away or retrospectively choose a D12 minimum-success threshold to avoid it.

In 600 additional synthetic trials, independent failures yielded **185/200 = 92.5%** coverage of the successful-attempt target; score-dependent failures yielded **190/200 = 95.0%** coverage of their true successful-attempt mean `1/3`, while the different all-attempt mean zero was covered **9/200**. A deliberately shared-random-shift model covered a marginal across-shift mean zero **41/200 = 20.5%**; this is **not** coverage conditional on fixed shared shift, so it must not be misrepresented as a direct test of the selected conditional target.

These results neither establish universal 95% coverage nor disprove the conditional Monte Carlo target. They motivate explicit assumption and finite-sample review before a scientific freeze. See `d13_synthetic_statistical_review_handoff_2026-11-15.md` for study details and provenance caveats.

## 4. Required Project Lead responses, in order

1. **Protocol/gate conformity:** Confirm that D12 reliability cutoffs may be selected only at their specified authorized pilot/bounded-revision gate, D13 post-pilot status is appropriate, and D14 operational settings are subject to applicable resource/precision authorization. Confirm the exact permitted original-data tier. A team selection is not a project-level freeze.
2. **D12 counting and sensitivity:** Confirm the precise definition/scope of distinct common original observations, treatment of missing or uncoded errors, the lowest admissible failed-fit sensitivity contribution, and the reliability comparison boundaries; reserve numeric `B_min`, `n_min`, `f_max` for the authorized pilot-dependent decision. Do not silently impose a cutoff in current development code.
3. **D13 inferential sufficiency:** Statistical reviewer determines whether conditional primary-attempt independence/exchangeability supports secondary resampling of successful Q scores and accepts or explicitly rejects finite-sample behavior, especially skewed n=24. Rejecting requires an authorized revision, not an implementation tweak.
4. **D14 seed contract:** Specify Branch B-owned namespaced derivation (separate observable tiers, dataset/replicate roles, primary vs secondary bootstrap, replay of individual attempts, collision/role isolation requirements). Confirm whether proposed seed 36 is final. Do not use or request generator-owned seeds or inaccessible hidden condition identifiers.
5. **D14 time/resources:** Specify authoritative timing scope, hardware/threads reference, golden-case selection using only permitted observables, actual numeric size scaling, timeout accounting and failure classifications, and justification/permission for proposed 2× runtime scaling. Confirm whether a proposed `B=500` meets the applicable Monte Carlo precision/resource gate or if an approved adjustment is required. No performance-dependent retroactive freeze.
6. **Evidence and execution:** Review source hashes, Python 3.14 JUnit and environment, original run failure ledgers, and pending production Common-Fitter conformance. Authorize any next pilot step only through its own documented gate, then freeze exactly approved artifacts with version, timestamp and checksum in the registered process.

## 5. Implementation boundary

Current public-repo development code includes `bootstrap/engine.py`, `development_attempt_diagnostics.py`, `development_reliability_audit.py`, and `development_seed_replay_audit.py`, plus synthetic regression tests. These inspect existing observable-side records and seeds. Their results cannot establish an approved D12 reliability decision because the cutoffs and common-observation rule are not yet frozen. The D14 replay verifier checks the *current* engine stream rather than proposing a new production namespacing convention. The D13 development interval remains separate from production support decisions, and the production Common Fitter remains fail-closed.

**Immediate review outcome requested:** Project Lead/statistical reviewer should annotate each of items 1–6 as **approved**, **revision requested**, or **deferred to specified gate**, identifying the applicable freeze record. Do not mark any public freeze registry row approved solely on the basis of this package.

**Public pre-write verification of actual document:** Contains only Branch B-allowed team decisions, explicit public observable-side bootstrap rules, user-provided aggregate generic synthetic development results, publicly inspected existing development-engine behavior, and unresolved project approvals. Contains no restricted generator code, configurations, generator-owned seeds, latent labels, true hierarchy, hidden condition mapping, sealed evaluation information or side-channel inference. Safe for disclosure in the shared public review repository.
