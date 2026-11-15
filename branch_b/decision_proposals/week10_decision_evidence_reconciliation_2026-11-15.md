# Branch B Week 10 — decision and evidence reconciliation (2026-11-15)

Status: project-lead discussion and implementation handoff, **not** a scientific freeze,
pilot authorization, production approval, or amendment to the governing protocol.
Review scope: permitted Branch B observable-side sources only.

## Basis and boundaries

- `Branch B Meeting Goals - Weeks 9-11 - November 2026.pdf`, Week 10 goals dated November 15, with substantive revisions targeted by November 18.
- Controlling `Version 2 Branch B Packet.pdf`, especially sections 2.2–2.5 and Appendices C.2, D and H.8.
- Existing Branch B draft cards, `decision_proposals/branch_b_meeting_intake_2026-10-20.md`, `week9_pl_completion_2026-11-08.md`, `common_fitter_development_readiness_audit_2026-11-15.md`, `numerical_interface_conformance_review_2026-11-15.md`.
- `governance/freeze_registry.csv`, as inspected from the shared source tree.

This review neither inspects restricted generating information nor assumes that a
proposal or passing development test constitutes approval. Team-reported
Python 3.14 successes are not independently inspected JUnit/environment records.

## Week 10 goal matrix

| Meeting goal | Already defined or recorded | Outstanding evidence, decision or gate |
| --- | --- | --- |
| Resolve core-algorithm ambiguities and verify worked examples | D01 fixed-input-denominator objective, beta=5, D03 projected AMSGrad, D04 exact hierarchy-balanced average, D05 1e-6/5 and 1000 updates, D06 product masses and distinct IDs are recorded; synthetic Python 3.14 passes reported | Final source-conformance and integrated review; D04 scalability; exact tree numerical comparison; registered production fitter still fail-closed |
| Correlation admissibility | Correlation Geometry Card uses 12 raw feature profiles, Pearson `1-corr`, exactly constant rejection; D08 historical choice favors relative centered-norm measure; a 1e-12 threshold is proposed | No approved quantitative near-constant statistic/threshold and dataset-level eligibility freeze located in inspected card/registry; confirm approval and applicable timing |
| Valuation sanity | Valuation/Chebyshev card uses training-only ddof=0 standardization, all 12 observable features and Chebyshev metric; no preliminary hierarchy | Favorable-feature sanity invariant, metric, minimum criterion, and pre-inspection chronology still require authorized evidence; D09 not closed by the implementation |
| Parameter selection and Common-Fitter selection, including failures/missing values/ties | Protocol permits validation selection only among complete candidates, one fitter shared across geometries, geometry-neutral rank-based/scale-invariant aggregate, no hidden truth or raw cross-geometry distortion pooling; D11 historical lexicographic proposal exists | Specify and freeze fully executable candidates, ordering, eligibility, missing/failure handling, tie breaking, exact quantities and prescribed time gate; no performance-based retroactive changes |
| Bootstrap interval target, calculation, confidence and reliability | Protocol fixes the successful-fit conditional `Q_b=S_b-min(D_b,1)`, point estimate mean successful `Q_b`; separate failure rate; indeterminate if minimum success/common observations unmet; at least 100 bootstrap repeats in full experiment; average ranks for tied Spearman statistics | D13 percentile interval is a proposal, not yet a verified CI for **mean** Q; target, confidence level, percentile algorithm, minimum successes/common IDs and failure sensitivity require pilot/bounded revision approval |
| Calibration quantiles, seed derivation, timeout scaling | Protocol requires family-specific score-level empirical 95th percentiles for each geometry × fitter, project threshold maximum across families; equality with threshold indeterminate; D14 mentions Branch B-owned seed 36 and proposed B=500, D15 inverse empirical-CDF proposal | Quantile tie/index convention, minimum usable calibration scores, namespaced seed derivation, exact deadline sizing/hardware, failure classification and authorized pilot-derived freeze remain to be finalized; never reinterpret a development benchmark as pilot timeout |
| Pilot-dependent numerical settings | Validator currently uses default `1e-12` matrix tolerance; historical D07 numerical proposal also uses `1e-12`; code characterization tests reported passing | Registry's numerical-tolerances freeze is pending. Near-symmetric upper-triangle reciprocal checks are orientation-dependent; numeric ultrametric/tree comparison and canonicalization require explicit authorized reconciliation |
| Final comparisons: CIs, multiplicity and region claims | Protocol defines interval-based support decision: lower > threshold = supported, upper < threshold = not supported, otherwise indeterminate; equality indeterminate; geometry-/family-specific false-support reporting; raw scores not directly comparable across geometries | Any pooled support claim needs a prior multiplicity rule; otherwise remain geometry-specific. Confirm frozen uncertainty procedures and any permitted region-level claim/reporting definitions before confirmatory use |
| D16–D17 and substantive revisions by November 18 | October 20 decision intake explicitly deferred D16–D17; Week 10 schedule explicitly assigns closure by November 18 | Neither item is demonstrated resolved by inspected Branch B records; obtain exact current controlling decision text, owner and approved freeze evidence rather than inventing content from decision numbers |

## Decision taxonomy

**Approved development direction but not full scientific freeze:** D01–D06 as
recorded in November 8 card/PL reconciliation. Do not reopen these solely due
to later performance.

**Protocol-defined constraints (not discretionary):** train-estimated
preprocessing; validation-only prespecified selection; one Common Fitter across
primary geometries; no hidden-truth-dependent tuning; bootstrap distinct
original identities and replicate-level uncertainty; family-specific
calibration and interval-based decisions; separate numerical failure reporting;
no locked-test processing prior to gate.

**Proposal or evidence incomplete:** D07/D08 numerical and correlation
admissibility; D09 valuation sanity; D11 selection details; D12/D13
bootstrap reliability and interval procedure; D14 resource and seed contract;
D15 empirical quantile convention; D16–D17; final comparability and
multiplicity permissions. This list describes the reviewed sources, not proof
that no later approval exists elsewhere.

## Work before November 18

1. Confirm whether the project lead has newer authorized records for D07–D17,
   especially the deferred D16–D17 definitions; retain existing method choices.
2. Draft exact executable formulas, eligibility conditions, missing/failure
   handling, deterministic tie resolution and examples for proposed D11–D15
   where the protocol permits Branch B specification. Mark proposed versus approved.
3. Reconcile correlation admissibility, valuation sanity and numerical
   conventions with the currently pending freeze entries before any required
   controlled inspection or pilot exchange.
4. Complete Python 3.14 source/environment/JUnit/checksum evidence collection.
   No change in metadata alone substitutes for an actual 3.14 run.
5. Obtain the authorized project-lead approvals at the applicable gates; do
   not substitute this checklist for the controlling packet or execution schedule.

## Public-write safety verification

The actual contents above contain only permitted observable-side scientific
specification summaries, existing public development decisions, and generic
procedural status. There are no hidden generators, latent labels, true tree,
sealed evaluation information, generator-owned seeds, restricted conditions,
or identifying side-channel analysis. Safe for public Branch B review.
