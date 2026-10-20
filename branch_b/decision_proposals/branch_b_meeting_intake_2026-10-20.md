# Branch B scientific decision intake — 2026-10-20

Status: **meeting selections received; not an approved protocol revision, executable freeze, or processing authorization**.

This is a faithful record of the Branch B team's choices against the 19 October 2026 scientific-decision discussion brief. The numbered options refer to that brief. Scientific implementation is limited to choices that can be reconciled with the controlling Version 2 Branch B Packet, existing approved freeze records, and the applicable timing gates. Do not treat an option label alone as an executable specification.

| Item | Team response | Reconciliation / outstanding executable specification |
| --- | --- | --- |
| D01 | Option A | Fixed input-weight denominator, explicit endpoint average, edge mean; exact soft-area/gradient and mass extension still required. |
| D02 | Start beta=5; calibrate during training-phase data | Initial slope candidate 5 recorded. The permissible data tier, optimization target, allowed beta candidates/range, selection statistic, and pre-pilot freeze deadline need authorization. Do not tune beta using validation/test, pilot performance, calibration, or locked data contrary to protocol. |
| D03 | Option B | Direct nonnegative weights with specified projection, rather than inverse-softplus initialization. Need exact projection (e.g. clamp), initial effective weights, optimizer-step order, zero handling, and confirmation of departure from the registered source-conformance default. |
| D04 | Option B | Average selected limiting gradients across admissible tied resolutions. The admissible limiting-gradient set, averaging measure, complexity bound, and deterministic relabeling behavior are not defined by the option label; do not substitute a naive average over all tied edges. |
| D05 | Option A | Return last iterate meeting the recorded stopping condition. Still need fully specified AMSGrad arithmetic, objective floor, precision, device, and tree conversion. |
| D06 | Option A, with further investigation; multiplicity must not scale weights linearly | Original-ID-based mass representation proposed, **weighting unresolved**. The option's illustrative pair weight m_i m_j is NOT approved; neither linear mass weighting nor product weighting may be assumed. Specify soft mass, pair weights, self-pairs, preprocessing and distortion before implementation. |
| D07 | Start 1e-12, calibrate during training-phase data | Provisional absolute comparison tolerance. Specify all predicates, scale/units, tie grouping, permissible calibration evidence and criterion, and freeze timing. No post-hoc tolerance changes on performance. |
| D08 | Option A | Relative centered-norm admissibility statistic. Must confirm threshold, equality boundary, zero raw norm, dataset-level eligibility, and relation to prior 0.95 CI discussion. The brief's 1e-12 is a candidate, not implied by the option label. |
| D09 | Option B | Single recovery-number favorable-feature criterion. Requires the exact metric, minimum, control identity/eligible permitted disclosure, verifier, and proof the choice predates inspection. Cannot substitute the exact-ultrametric positive-control threshold without explicit approval. |
| D10 | Option B; 0.05 | Proposed minimum meaningful **absolute rooted-triplet accuracy difference** 0.05. Historical freeze/inspection chronology and substantive rationale remain unresolved. A new record cannot retroactively satisfy a required pre-inspection freeze. |
| D11 | Option B; team questions need due to training phase | Lexicographic failure/distortion/stability/resource Common-Fitter selection is the proposed choice. The protocol still requires one geometry-neutral, scale-invariant, ground-truth-free selection rule and its pre-pilot freeze; having a training phase does not waive it. Specify ordering, quantities, eligibility, failures, missingness and ties. |
| D12 | Option A | Fixed attempt budget with strict reliability requirements. Minimum successes, common-observation count, maximum failure fraction and failure-code mapping remain to be fixed at the permitted gate. |
| D13 | Option A | Percentile interval from successful Q bootstrap scores. Explicitly distinguish conditional replicate-score spread from a confidence interval for mean Q; require approved inferential target, confidence level, percentile convention and failure sensitivity. |
| D14 | Timeout: twice golden-case runtime, scale for different input count; seed 36; B=500, calibrate during training phase | Proposed operational plan only. Specify timing scope, reference hardware, scale function and size variables, memory/threads, representative golden case, permitted pilot measurement and freeze; master seed 36 is Branch B-owned only and requires deterministic namespaced derivation, disjoint tier roles, and recording; B=500 is proposed, subject to permitted resource/precision gate. Do not replace the protocol's default planned Monte Carlo count. |
| D15 | Option A | Inverse empirical-CDF order-statistic calibration quantile. Freeze tie/index convention, minimum usable count, failure handling and family inventory before authorized calibration. |
| D16–D17 | Deferred | Not decided or implemented. Preserve their future freeze/approval deadlines. |

## Immediate implementation status

The 19 October executed final audit found three decision-independent checked-path defects (F1–F3). Bounded code and synthetic regression changes to reject undeclared terminal vertices, lossy masked/Boolean matrices and nonfinite diagnostics were committed on 20 October. These changes do not implement a new scientific method, change a numerical tolerance, or authorize pilot/calibration processing. Python 3.14 CI verification must be inspected before claiming the repairs are tested.

## Required scientific clarifications

1. **Training-phase calibration** (D02, D07, D14): which protocol-defined observable tier is meant, which metric may guide each choice, and by what date/gate must each be frozen? Do not infer authority to tune from the word “training.”
2. **D06**: approve a mathematically complete non-linear multiplicity/soft-mass weighting, including self-pairs and interaction with preprocessing and validation, or authorize a specified design investigation without changing the production fitter.
3. **D04**: define an exact admissible limiting-gradient average and complexity treatment at ties.
4. **D09–D10**: define the favorable-feature recovery criterion and its permitted verification; reconcile the historical minimum-effect freeze chronology.
5. **D11**: record a concrete common-fitter selection rule despite the availability of training data.
6. **D14**: specify a resource scaling formula and seed-derivation contract; secure the protocol-required pilot and bounded-revision gates.

No hidden generator, true hierarchy, sealed ground truth, experimental conditions, or other blinded information was consulted for this intake. No production seed was used.