# Branch B Week 10 Method Specification: PL-Reviewed Revision

**Team draft:** 17 November 2026. **PL-reviewed revision:** 18 November 2026
**Status:** Project Lead review draft only. Not a scientific freeze, approval, pilot authorization, calibration run, independent validation, locked-test processing, or unblinding.
**Basis:** *Version 2 Branch B Packet*, §§2.2–2.4, Appendix C.2 (printed pp. 58–59), Appendix D (printed pp. 60–62), *Evaluation and Acceptance Protocol* (printed pp. 50–55); *Branch B Meeting Goals — Weeks 9–11*, Week 10/11; public Branch B team-selection and reconciliation notes dated 15 November 2026. In a conflict, controlling protocol and approved freezes govern.

## 1. Implementation baseline and reproducibility

- Public development branch: `branch-b-d06-integration-20261117`.
- Team-reported tested revision: `91fb66d7c6b780104d63abfcbc80e43cf92d9dc3` (842 passes). Latest inspected development revision: `51eca3158bff46bf52c04ec592c71559cb2ad637`, which adds five independent numerical oracle cases. A separate PL execution under Python 3.14.10 / NumPy 2.5.3 / pytest 8.4.2 passed 847 tests with zero failures/errors/skips. These are different source checkpoints, not additive test totals.
- User-reported actual local environment: Python **3.14.10**; full regression **842 passed** in **8.65 seconds**. JUnit XML, version, pip check, pip freeze, commit ID, local Git status and JUnit SHA-256 were saved outside the public repo in `branch-b-d06-runner-evidence`. These claims are based on user-supplied terminal output; original evidence artifacts were not independently inspected for this draft.
- Changes: development distinct-original LCA stability adapter and development D06 bootstrap runner, with synthetic tests. The runner delegates attempted-replicate enumeration/failure recording to existing engine, reuses the D06 distinct-ID boundary and development split orchestrator, and defers test input conversion until after validation selection.
- **Not established by tests:** production Common-Fitter activation, integrated numerical certification, scientific interval coverage, calibration readiness, complete freeze records, pilot authorization, independent validation or locked-test eligibility.

## 2. Geometry and one Common Fitter

**Protocol-fixed:** Confirmatory geometries require complete Geometry Cards defining executable observable-state-to-dissimilarity maps, preprocessing, admissibility, train-estimated parameters, validation selection, failures, version/complexity and favorable-feature sanity. The valuation geometry cannot use hidden labels or a preliminary fitted hierarchy in defining native distance. The common post-geometry normalization must preserve finite off-diagonal ordering. Geometry-specific selection is frozen before hierarchy-support calibration. The single selected Common Fitter and tree extraction are shared by all confirmatory primary geometries. Raw distortion values across geometries cannot be pooled for fitter selection. Cards and relevant gate records must be complete by their respective required stages (packet §2.2–2.3; Appendix C).

**Branch B team direction (not PL freeze):** D11 registers exactly one Common-Fitter candidate, the existing gradient-descent min-max method with D01–D06 development choices. If it meets every independently required eligibility/conformance gate, it is the only eligible fitter for all registered primary geometries. If it fails, do not introduce a fallback or an alternative ranking. The existing production fitter remains fail-closed pending approval/certification. D06 uses distinct original identities and multiplicity product weights for distinct pairs, retaining all resampled rows in train preprocessing.

**Still required:** The PL documentary review concurs with the singleton interpretation; the registry and draft card have been reconciled. Remaining requirements are a fully approved Common Fitter Card, source/conformance reconciliation, exact numerical/tie/degenerate behavior, numerical-failure mapping, version/complexity/timeouts and freeze records. D08 proposed Pearson-profile relative centered-norm admissibility is team-selected but pending formal approval. D09 valuation favorable-feature invariant, metric/minimum and timing remain open. D07 numerical tolerances also require authoritative freeze evidence.

## 3. Bootstrap, stability and reliability

**Protocol-fixed (Appendix D.2):** Independently resample the original train/validation/test splits; refit train-only preprocessing and representation on bootstrap train; reapply frozen geometry-specific validation selection on bootstrap validation; evaluate support on bootstrap test; do not reselect the geometry definition, common normalization, Common Fitter, tree extraction or support-score definition. Repeated draws contribute multiplicities, **not duplicate leaf identities**. LCA-depth stability compares shared distinct original observations, using average ranks for ties. Record every failed, timed-out, nonfinite, malformed, excluded-degenerate, insufficient-common-observation, or undefined-rank attempt; do not silently discard failure records. Bootstrap unsuccessful attempts do not enter the successful-score interval, but must remain in total-attempt failure reporting.

For a successful attempt `b`: `Q_b = S_b - min(D_b, 1)`. The support point estimate `Qhat` is the arithmetic mean of successful `Q_b` values. The bootstrap support interval is conditional on successful attempts. Report the failed-attempt proportion separately. When reliability is not met, the support decision is indeterminate. A prespecified lowest-admissible-contribution sensitivity analysis for failed fits is required, but its executable treatment must be confirmed under the applicable freeze.

**Team-selected proposals (not project-level freeze):** D12 uses fixed attempted budget `B`, successful count `B_s`, failures `B_f=B-B_s`, failure fraction `B_f/B`, minimum success `B_min`, minimum distinct common IDs `n_min` and maximum failure fraction `f_max`. D13 proposes a nominal two-sided 95% percentile interval for the conditional mean of successful Q: draw **10,000** secondary resamples with replacement, each of length `B_s`, calculate their means, sort, and return the **250th and 9750th** order statistics (one-based; no interpolation). This is **not** a certified population-level 95% interval or guaranteed finite-sample coverage. Synthetic diagnostic evidence includes undercoverage in a small skewed-score cell; preserve this warning and obtain statistical review rather than tuning thresholds retrospectively.

**Still required:** pilot-authorized numeric `B_min`, `n_min`, `f_max`, The PL review defines each attempt's common set as eligible distinct original test IDs present in both its bootstrap tree and the full-test reference; count identities once before admitting a successful score. From S in [-1,1] and D>=0, the existing Q definition has lower bound -2. For complete B-attempt execution the failed-fit sensitivity point summary is `(sum_success Q_b - 2*B_f)/B`. This derived summary is separate from the successful-only interval. Remaining requirements include a complete sensitivity interval/decision procedure, evidence for interval assumptions and conditional Monte Carlo interpretation, a recorded secondary-resampling seed namespace, failure semantics and post-pilot freeze. D14 proposed master seed 36, `B=500` and a timeout related to 2x golden-case runtime with input-size adjustment are **not** yet executable approved values: namespace derivation, source hardware, numerical scaling, reference cases and gate authorization remain open. Current development seed replay is not a frozen production seed contract.

## 4. Support calibration and decisions

**Protocol-fixed (Appendix D.3):** For every registered primary geometry × candidate fitter, calculate an empirical 95th percentile separately within every prespecified nonhierarchical calibration family, then use the **maximum family percentile** for that geometry × fitter threshold. Freeze all candidate thresholds before blind validation; after selecting the fitter, mechanically select the corresponding precomputed threshold without recalibration. Calibration, independent null validation and locked null test banks are disjoint at realization and seed level. Calibration-bank false-supported rates are construction diagnostics, **not** independent evidence of false-support control. Independent null validation requires a previously frozen overall and family-specific decision-level acceptance rule; a failure blocks confirmatory support claims for the affected procedure, not a retune or replacement.

For support interval `[L,U]` and threshold `q`: **supported** when `L > q`; **not supported** when `U < q`; **indeterminate** otherwise, including equality and failed reliability. The successful-score point estimate does not override the interval decision. Raw support scores are not directly comparable across geometries.

**D15 team-selected proposal (not PL freeze):** On the finite eligible successful scores for a specified family and geometry × fitter, the percentile is order statistic `ceil(0.95*N)` (one-based nearest rank, without interpolation), keeping tied values. Preserve every calibration attempt and required family. If any required family lacks its *approved* minimum usable count, calibration is incomplete; never drop that family to obtain a threshold.

**Still required:** exact authorized calibration family inventory/tier and minimum usable score count, score and failure eligibility criteria, independent null-validation acceptance thresholds/confidence rules, seed provenance, approval before calibration, and freeze evidence. No calibration run is authorized by this draft.

## 5. Final recovery comparisons and scientific claims

**Protocol-fixed (printed pp. 50–55):** Primary recovery metric is observation-level rooted triplet accuracy on triplets resolved in the true planted tree, calculated **only by authorized evaluation personnel and at the permitted evaluation stage**. An unresolved estimated triplet is incorrect in the primary analysis. Primary valuation-vs-comparison inference uses *paired Monte Carlo replicates* for each comparator: `D_r(g) = A_val,r - A_g,r`. Scheduled geometry-level numerical/procedure failures receive accuracy `A=0` for the failure-penalized primary paired contrast; retain geometry-specific failure frequencies and successful-only sensitivity results. Do not treat triplets, observations or pairs as independent replicates. Confidence method/level, denominators and failure handling are frozen before locked generation. Comparisons against each comparator are confirmatory individually; best-comparator and omnibus/family advantages are secondary absent a prespecified multiplicity-adjusted rule. No locked test analysis or true-tree-dependent evaluation is Branch B development work.

**Scientific-claim gates:** A claimed valuation advantage requires locked-test evidence, a previously frozen meaningful minimum effect, CI excluding zero, an eligible frozen contiguous region or deterministic preselected region rule, and sensitivity robustness. Region adjacency differs by exactly one ordered level in exactly one of the three grid coordinates, holding the other two fixed. Post-hoc selected regions are exploratory. The favorable exact-ultrametric procedure-control rooted-triplet target is 0.95 under the frozen common normalization/fitter/extraction; the separate valuation favorable-feature sanity invariant remains a distinct gate. Null false-supported rates, indeterminate rates and family-specific reporting are mandatory.

**Still required:** verify historical minimum-effect freeze provenance (including any proposed 0.05 value), confirmed comparator/region inventory and permitted region-selection rule, paired CI and multiplicity conventions, failure-code applicability and final evaluation-team-owned procedures. Do not backfill these using recovery outcomes.

## 6. Decision register and handoff requests

| Item | Current state | Next authoritative action |
|---|---|---|
| D01–D06 | Recorded development direction; D06 development bootstrap path tested | Finish production-source conformance, Common Fitter Card and applicable method gates |
| D07–D08 | Team proposals consolidated; D08 documentary compatibility reviewed | D07 implementation placement/tree semantics; actual numerical/Geometry Card authorization, boundary evidence and freezes |
| D09 | Favorable-feature sanity criterion incomplete | PL-approved exact invariant, statistic, minimum and pre-inspection evidence |
| D10 | Minimum effect historical proposal/record needs provenance reconciliation | Verify pre-inspection freeze; do not tune from results |
| D11 | Exactly one fitter team-selected; PL documentary concurrence and card/registry reconciliation complete | Final scientific card/selection authorization and implementation certification |
| D12 | Fixed-attempt framework, common-ID scope and derived -2 support bound documented | Authorized numerical thresholds and complete sensitivity interval/decision freeze |
| D13 | Secondary-resampled mean 95% interval selected | Statistical/dependence review; seed and freeze approval |
| D14 | Operational seed/B/timeout direction proposed | Precise namespacing, sizing, hardware, resources, applicable approval gate |
| D15 | Nearest-rank and failed-score preservation team-selected | Minimum usable score/family inventory, approval and freeze |
| D16–D17 | Deferred, authoritative question text not yet recovered | Project Lead to supply original wording; do not invent proposals |

## 7. Week 11 delivery checklist

- Reconcile this draft against authorized PL comments and up-to-date approval/freeze records; do not silently replace existing choices.
- Provide executable method cards, pseudocode and small synthetic worked examples for D01–D15, with unresolved fields clearly marked rather than filled with guessed defaults.
- Record precise Python 3.14 source version, focused and full JUnit test evidence, dependency/environment records, manifest/checksums and known limitations. Preserve original failure attempts.
- Review all shared-repository changes for **actual Branch B permission and public-disclosure safety before each write**; never publish unreviewed machine-local evidence or restricted material.
- Hold pilot, calibration, independent-validation, locked-test and unblinding work behind their specific approval gates.

## 8. PL Review Disposition and Remaining Work

The technical/documentary review of this specification is complete. D11 singleton compatibility, the D08/D15 candidate definitions, D12 counting/accounting and the separation of protocol requirements from team proposals are supported within their stated scope. The scientific freeze remains a separate action tied to complete artifacts and actual decisions.

The new distinct-ID stability adapter and bootstrap runner close the earlier absence of a D06 development orchestration path. They preserve original IDs/multiplicities and defer test data until validation selection. Runner tests still use a recording fitter; their undefined-stability case is a star-tree failure. They do not demonstrate a successful full reference-stability run using the actual development optimizer. Required next evidence is a nonconstant, identity-bound reference/tree worked example with actual fitter output and retained failed attempts.

Complete D07 canonicalization in the intended entry point, reconcile historical D05 production defaults, and verify numeric matrix/tree agreement and registered failure export. The inspected D06 development fitter still reads one input triangle after historical validation. No production entry point was activated in this review.

The concrete proposed seed/paired-comparison/claim text remains in `week10_analysis_operations_draft_2026-11-16.md`. Incorporating its new rules requires explicit acceptance; this revision does not silently adopt them. D09/D10 historical evidence and the original D16/D17 questions remain unavailable in the inspected sources. Advisor follow-up is outside this task; excluding it does not waive an applicable gate.

Original team-proposed delivery dates are not treated as an approved schedule amendment. Current scientific-stage eligibility is determined by the packet and actual gate records.

Project Boundary: actual revised content was inspected and permitted for Branch B/public disclosure. It contains permitted protocol summaries, team proposals and aggregate development evidence only. No generating implementation, hidden parameters/mappings, restricted seeds, latent labels, sealed truth or restricted paths are included. This is a separately reviewed revision; the original uploaded attachment is preserved unchanged.
