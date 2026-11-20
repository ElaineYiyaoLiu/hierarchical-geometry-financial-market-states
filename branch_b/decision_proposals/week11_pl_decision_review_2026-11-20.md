# Week 11 Project Lead Decision Review

Prepared November 20, 2026. Review draft. Numerical candidates and decision fields below require the applicable approval.

## D09 Valuation-Geometry Sanity Check

The Geometry Card requires a prespecified native-dissimilarity invariant and a minimum structural-agreement or recovery criterion under the Common Fitter. Freeze the qualifying control, invariant, criterion and verifier before Branch B receives or inspects the designated control. The separate procedure positive-control criterion has its own scope.

**Candidate invariant.** On a qualifying favorable control with a prespecified split into groups, define W as the maximum native dissimilarity over within-group pairs and C as the minimum over between-group pairs. Require a finite, nonnegative, symmetric native matrix with zero diagonal, positive off-diagonal scale, and C > W. A tie at C = W fails this candidate strict separation check. Preserve the project numerical conventions and apply the registered common normalization before fitting. The evaluator needs the expected partition. The native geometry and fitter receive the observable inputs only.

**Candidate structural criterion.** For every prespecified control group, evaluate all rooted triplets with two eligible observations inside that group and one outside. Define R as the correctly resolved fraction of this prespecified inventory, counting unresolved triplets as incorrect. Report the inventory and denominator, and require a nonempty inventory. Missing output, invalid tree or failed fitter is an unsuccessful check. Approve the actual minimum R and the control-specific group/inventory definition before release or inspection. A development fixture can use the exact expected answer R = 1 to test the verifier.

**Arithmetic fixture for verifier review.** Use a separate train split with two rows equal to the all-minus-one and all-plus-one vectors in 12 coordinates. Coordinate-wise training standardization with ddof = 0 has mean zero and scale one. In the test split repeat each scalar across 12 coordinates for A = 0, B = 0.25, C = 2 and D = 2.25. The development Chebyshev reference yields within-group distances 0.25 for AB and CD. The minimum cross-group distance is 1.75, so the native gap is 1.50. The declared tree ((A,B),(C,D)) correctly resolves all four eligible triplets. A star resolves zero. These are verifier expectations from the arithmetic and declared tree. The actual Common Fitter was not run on this proposed example. The qualifying project control and the acceptance minimum remain pending.

**Evidence to retain.** Geometry and fitter revisions, preprocessing and selection bindings, qualifying-control reference and approved expected relations, dated approval and delivery/inspection record, complete eligible inventory, native distances, normalized scale, output tree, score and attempted failure record. Retain any restricted evidence through the authorized recorder.

## D10 And D16/D17 Source Reconciliation

| Item | Finding | Evidence required to close |
| --- | --- | --- |
| D10 minimum meaningful effect | The [October 4 reconciliation](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/blob/main/governance/minimum_effect_provenance_review_2026-10-04.md) records an unresolved value and chronology. No original approval or earliest inspection attestation was recovered in the available project records. | Original dated value, units, metric and substantive rationale, approving authority and freeze reference, earliest relevant development-contrast inspection attestation, and evidence that the freeze predates it and pilot exchange. Refer unresolved chronology for explicit protocol disposition. |
| D16 and D17 | The meeting agenda calls for resolution. The later PL record points to the October 19 decision brief. The authoritative wording was not recovered from the available records. | Original brief or dated faithful transcription, recorded separately for each question, with author, date, version and source. Keep both IDs open until then. |

The current paired-comparison, multiplicity and region drafts can be reviewed on their own terms. Keep their relation to D16/D17 pending until the original questions are recovered.

## D13 Statistical Review

**Disposition requested.** Record accept, revise, or defer for each item below, with rationale, decision owner, date and exact specification revision. Separate the support-interval decision from the final paired recovery comparison.

| Review item | Evidence or concrete choice |
| --- | --- |
| Estimand | Confirm whether the protocol calls for Monte Carlo uncertainty in the mean successful score conditional on fixed original data and the fixed reference procedure. Confirm whether actual attempt generation, preprocessing, selection and failure handling support the needed conditional exchangeability. |
| Candidate interval | Preserve the team candidate for review. It uses 10,000 secondary resamples of successful scores and one-based nearest ranks 250 and 9750 for a nominal 95% interval. The skewed n = 24 synthetic cell covered 368/400 trials (92.0%). Decide whether the stated limitation is acceptable at the intended reliability gate or a prespecified revision is needed. |
| Failure sensitivity | For a complete B-attempt ledger, set Y to Q for success and -2 for recorded failure. The fixed-ledger summary is mean(Y), equivalent to (sum of successful Q minus 2 times the failure count)/B. A candidate interval resamples B entries from the complete Y ledger using a separately approved deterministic secondary namespace. Use the same nominal ranks only if explicitly approved. The inferential target is the mean under the prespecified penalty. This construction leaves the successful-only interval and D12 reliability decision separate. |
| Decision and boundary cases | For review, a conservative candidate is to withhold a robustness claim when the approved penalized sensitivity decision disagrees with the successful-only support decision or is indeterminate. Record the chosen consequence and how the approved calibration reference is used. Treat incomplete ledgers as incomplete, show failure counts and denominators, and retain the D12 indeterminate outcome when reliability fails. With zero successes the penalty summary may equal -2 for a complete failure ledger, while the successful-only interval is undefined. |
| Evidence and authority | Record source, environment, assumptions, complete attempt and failure ledger, interval and sensitivity procedure, approved namespace, and statistical and PL disposition. Keep pilot-dependent reliability cutoffs for their applicable gate. |

See the [PL specification review](week10_specification_review_2026-11-18.md), [PL-reviewed specification](week10_method_specification_pl_revision_2026-11-18.md), and [Branch B geometry registry](../geometry_registry.md).

Project Boundary. The proposed fixture uses invented arithmetic values. The research controls and authorized evaluation stages are governed by their existing records.
