# Branch B: Weeks 1-6 evidence and execution checklist

Status: working evidence handoff, reconciled on 2026-10-19 against repository revision `64db636725f4c96c83f2ad0dc0658a12b1e077c7`. This is not a freeze record, method approval, or processing authorization.

Scientific requirements come from the controlling Version 2 Branch B Packet and approved freeze records. The Schedule supplies execution order and deliverables, not replacement scientific rules. This review used the packet's Sections 2.1-2.5 and Appendices C-D, the Schedule's Weeks 1-6, and the public Branch B records linked below. It is not an exhaustive audit of every approval surface or historical code change.

## Reconciled status

| Stage | Evidence now located | Remaining requirement |
| --- | --- | --- |
| Week 1: setup | [Registry](geometry_registry.md), [draft cards](draft_cards/), [environment record](branch_b_environment.txt), [seed policy](seed_namespace_b.yaml), [schema pass report](schema_report_b.json), and [acknowledgement](handoff_acknowledgement.md). The acknowledgement is GIVEN; the October 2 preflight records the Week 1 gate as complete. | Preserve these historical records. Setup completion is not pilot-exchange approval or a complete scientific runtime. Production seed values are not supplied by development fixtures. |
| Week 2: implementation | Preprocessing, distance primitives, normalization, pipeline orchestration, bootstrap plumbing, support/recovery/output helpers, and synthetic tests are present. The latest detailed CI report verifies the tested development suite under CPython 3.14.8. | The complete executable Common Fitter and reserved numerical/admissibility specifications still block integration readiness. Passing stub-based tests does not close this gate. |
| Week 3: pre-pilot methods | Source-conformance review, exact fitter-paper reference map, numerical proposals, and development validation reports are available. | Complete executable cards and end-to-end golden reports; prespecify and satisfy valuation sanity; reconcile correlation admissibility; freeze geometry search and geometry-neutral fitter-selection rules at their required gates. |
| Week 4: pilot | Development packaging and failure/provenance tooling have verified evidence. No scientific pilot completion is established by those records. | Complete pre-pilot methods, obtain the designated pilot-exchange approvals and permitted bank receipt, then execute the frozen pilot and record operational benchmarks and exit evidence. |
| Week 5: calibration | Existing infrastructure can support later bookkeeping; it is not a calibration result. | Pilot exit, the permitted bounded operational revision, approval/checksum freeze, Gate 5A, and authorized calibration-bank receipt precede official processing and threshold calculation. |
| Week 6: selection and runner | A reviewed four-file packaging-component snapshot was built reproducibly. It is not the scientific validation runner. | Authorized blind validation, the frozen common selection rule, mechanically activated precomputed thresholds, and a complete tested scientific runner with designated approvals. |

A missing or unreconciled approval is **unverified**, not proof of a failed gate. This checklist does not infer authorization from a calendar date, a file's presence, or a passing CI badge.

## Verified development evidence index

| Completed engineering work | Evidence and scope |
| --- | --- |
| Accumulated min-max/Jacobian, validation, tree, and pipeline tests; two incorrect test assertions corrected with failures retained | [Development validation](development_validation_2026-10-19.md) |
| Canonical development ZIP builder/verifier and synthetic integrity tests | [Bundle validation](development_bundle_validation_2026-10-19.md) |
| Actual reviewed packaging source built twice in separate Python processes with matching bytes and provenance | [Source snapshot validation](packaging_source_snapshot_validation_2026-10-19.md) |
| Bootstrap evaluator-seed retention and protection of original sampled indices | [Bootstrap provenance validation](bootstrap_provenance_validation_2026-10-19.md) |
| Snapshots of returned preprocessing/fitter records across splits, candidates, calls, and bootstrap attempts | [Pipeline output snapshot validation](pipeline_output_snapshot_validation_2026-10-19.md) |

The latest detailed test evidence above is for code revision `8f224c2fcaa48ba9b915a2240421fc1f175cfb1c`: Branch B support/recovery/failure suite **202 passed**, shared validator **15 passed**, and repository-wide discovery **343 passed**, all under CPython 3.14.8. The first two results are from run `39320669279`; repository-wide discovery is from run `39320669222`. The suites overlap and the counts must not be added. These are retained prior execution results, not a new test run produced by this reconciliation.

Each report retains its own tested revision, actual environment, limits, and artifact checksum. The pinned packaging snapshot still contains only its four reviewed packaging-related files at source revision `6975d4da8baf1e1374353466fe8420183da69152`; later pipeline changes have not been silently substituted into that archive. Previous failures and historical environment records remain part of the provenance.

## Decisions and evidence needed to resume substantial work

| Blocking specification | Required resolution, without choosing it here | Work it unlocks |
| --- | --- | --- |
| Common Fitter: CF-SIGMOID, CF-INIT, CF-POSITIVITY | Record the authorized sigmoid convention, initialization, and nonnegativity parameterization and their interaction. Complete the executable loss/gradient specification, including the apparent equation/pseudocode differences already flagged in the paper map. | Source-faithful optimizer implementation, actual Python 3.14 dependency validation, and end-to-end fitter golden tests. |
| Numerical comparison conventions | Resolve the separately pending symmetry, diagonal, ultrametric-validity, and height-tie comparisons. The approved normalization and reciprocal-weight thresholds do not automatically approve these other tolerances. | Conformance checks and numerical boundary cases against a controlling specification. |
| Correlation admissibility | Locate and reconcile any approved decision, or finalize the quantitative rule and deterministic failure/eligibility handling. The earlier 0.95 confidence-level discussion alone is not a complete near-constant rule. Do not reinstate the rolled-back quantile construction automatically. | Complete correlation card and eligibility tests without inventing a threshold or repairing observations. |
| Valuation sanity | Prespecify the favorable-feature invariant and minimum criterion before inspecting the designated control, and obtain the required sanity evidence through the permitted process. | Completion of the valuation Geometry Card and its pre-pilot sanity gate. |
| Geometry search and common selection | Locate approved rules or finalize them at the designated gate. Common-Fitter aggregation must be geometry-neutral and scale-invariant, with explicit failure, missing-quantity, incomplete-coverage, and tie handling. Do not equate the pipeline's injected selector with a frozen selection rule. | Complete pilot configuration and, after calibration/authorization, legitimate blind-validation selection. |
| Pilot-dependent operational rules and later approvals | Fix bootstrap success/common-observation requirements, interval/failure handling, timeout, and seed rules at the protocol-assigned stage; do not prematurely freeze them here. Reconcile the required exchange, exit, revision, calibration, and selection approvals in order. | Official pilot/calibration/validation execution and scientific runner certification. |

Controlling Branch B evidence for this list:

- [October 2 preflight](week2_preflight.json) and [numerical proposals](decision_proposals/week3_numerical_rules_proposal.md).
- [Common-Fitter Card](draft_cards/gradient_descent_common_fitter.md), [source-conformance decisions](decision_proposals/common_fitter_source_conformance_2026-10-02.md), and [paper reference map](decision_proposals/common_fitter_paper_page_map_2026-10-19.md).
- [Correlation card](draft_cards/correlation_distance.md), [valuation card](draft_cards/valuation_geometry.md), and [pre-pilot source reconciliation](pre_pilot_source_reconciliation_2026-10-18.md).

The October 2 preflight's CI-pending entries are historical. Later development reports supply additional execution evidence, not blanket scientific acceptance of the implementation. Its explicit unresolved scientific specifications have not been approved by newer unit tests. A newer governing approval must be read and reconciled before changing this assessment.

## Stopping point and resumption

After this evidence reconciliation, no further substantial decision-independent implementation step toward the pending Weeks 1-6 gates has been identified. Routine additional defensive tests or another packaging layer would not resolve the missing method specifications. Pause autonomous implementation rather than present those activities as scientific milestone completion.

This is a task-prioritization checkpoint, not a new protocol freeze or a claim that every possible defect has been eliminated. Resume when an authorized method decision or previously missing controlling record is available, or when a demonstrated material implementation defect warrants a bounded correction.

The next substantive sequence is: resolve the earliest method specifications; implement and validate them under Python 3.14; complete the pre-pilot method/golden package; obtain the required pilot authorization; and only then follow the Schedule's pilot-exit, Gate 5A, calibration, blind-selection, and runner-certification sequence. No approval or scientific result is manufactured by this handoff.
