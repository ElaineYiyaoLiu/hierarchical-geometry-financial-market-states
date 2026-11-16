# D12-D14 Project Lead Review Disposition

Review date: November 15, 2026 (America/New_York). Execution evidence uses UTC dates; the evidence directory is `../reviews/2026-11-16-pl/`.

Reviewed source: `74954ae5126e5967e700234a8ccd8d5379a8e9f6`, Branch B's November 15 handoff. Elaine authorized completion of the available PL review and verification work. This record completes the documentary review and identifies the remaining scientific and operational gates. It does not record a new parameter, seed-rule, schema, evaluation-definition or protocol freeze.

## Responses to the Six Requested Decisions

| Item | Disposition | Completed review or required next evidence |
| --- | --- | --- |
| 1. Protocol and gate conformity | Review completed; numerical freeze deferred to specified gate | Sections 2.4-2.5 and Appendices D.2, G.4 and H.8 of the Version 2 Branch B Packet control. Successful-fit scoring, separate failure reporting, failed-fit sensitivity and distinct test-observation identities are required. The pilot/bounded revision must supply its designated numerical choices before scientific processing at later gates. |
| 2. D12 counting and sensitivity | Protocol meaning clarified; integration revision requested; numerical cutoffs deferred | The common set is the original test identities represented in both the full-test fit and that replicate's bootstrap-test fit. Count identities once. A replicate with insufficient eligible common observations is unsuccessful. The score's lower admissible bound is -2 under valid S and nonnegative D. Complete the identity-bound integration and sensitivity reporting described below. |
| 3. D13 inferential sufficiency | Computational review completed; scientific acceptance deferred with explicit revisions required | The candidate computes resampled means using the selected 10,000 resamples and ranks 250/9750. Its target must remain explicitly conditional Monte Carlo uncertainty. Document the actual evaluator's conditioning and independence assumptions, retain the observed small-sample undercoverage, and complete the authorized statistical/pilot review before scientific use. |
| 4. D14 seed contract | Existing development replay checked; production contract revision requested | Existing `SeedSequence(base_seed).spawn(B)` replay is characterized. Production tier/dataset/role namespacing is incomplete. Supply the exact versioned derivation, reference vectors and isolated-attempt replay before approval. No production seed value is selected here. |
| 5. D14 timing and resources | Deferred to authorized feasibility/precision gate; specification checklist completed | No numeric timeout or scaling law can be justified from this handoff alone. Record benchmark scope, observable size variables, hardware/threads, timeout accounting, and resource/precision evidence. B=500 and 2x golden runtime remain proposals. |
| 6. Evidence and execution | Independent development verification completed within archived scope; production authorization withheld | See the execution report, original JUnit, dependency freeze, study journals, audit results and hashes. These are new runs of the reviewed source, not authentication of inaccessible original workstation files. The Common Fitter and D06 scientific integration still require their own conformance gate. |

None of these items creates an approval entry in `freeze_registry.csv` or `approval_evidence_register.csv`. Those registers remain unchanged.

## D12: Protocol Requirements and Derived Quantities

Let I_full be the original test identities in the full-test reference tree. For primary attempt b, let I_b be the distinct original test identities in its bootstrap tree. The comparison uses C_b = I_full intersect I_b and n_common,b = |C_b|. When the full tree covers all original test observations, this equals the number of distinct originals represented in the bootstrap test fit. It is not an intersection of training, validation and test splits, a count of pairs, a count of duplicate leaves, or an average across attempts. Average ranks apply to tied LCA-depth comparisons.

Appendix D.2 makes an attempt unsuccessful when its common-observation set is below the frozen minimum, its rank comparison is constant or undefined, its score is nonfinite, its tree is excluded, it times out, or its output fails the applicable checks. Preserve the original draw, multiplicities, seed and diagnostics for every attempt. An uncoded error remains visible as an unsuccessful/error record requiring mapping review; it must not be dropped, assigned a successful score, or silently treated as an approved failure-code mapping.

For a fixed attempted budget B, retain B_s successful and B_f unsuccessful attempts with B = B_s + B_f. Failure rate is B_f/B. The team's proposed inclusive comparisons are B_s >= B_min and B_f/B <= f_max; numeric B_min, n_min and f_max remain for their authorized gate. Evaluate per-attempt common-set eligibility before counting B_s. A missing reliability rule cannot support a scientific reliability assertion. Incomplete execution must be reported as incomplete, with missing/unexecuted attempts distinguished from observed fit failures.

For valid successful scores, S is in [-1,1], D >= 0 and Q = S - min(D,1), so Q is in [-2,1]. Thus -2 is the mathematical lowest admissible contribution under the existing definition, rather than an empirically tuned penalty. The corresponding finite-attempt sensitivity point summary is:

`Q_sensitivity = (sum_success Q_b - 2*B_f)/B`.

Example: B=5, successful Q values 0.2, 0.4, 0.6 and two failed fits give Q_hat=0.4, failure rate=0.4 and Q_sensitivity=-0.56. This illustrates accounting; it selects no reliability cutoff.

The primary interval remains conditional on successful scores. Do not relabel it as an interval for Q_sensitivity. Appendix D.2 also requires reporting whether the support conclusion changes under failed-fit sensitivity. The exact sensitivity interval and decision procedure must be prespecified and reconciled at the designated gate. The point summary alone does not complete that requirement. The bound derivation does not modify production failure handling.

Current development distinct-position diagnostics and `summarize_successful_support(...).reliable_for_interval` are insufficient for complete D12 certification: the latter checks a minimum success count only. Production integration needs the common-identity, failure-fraction and full sensitivity predicates as well as the approved threshold record.

## D13: Target, Assumptions and Review Finding

Write X for the fixed permitted original data, R for the fixed reference procedure/output and A_b for primary-attempt success. The proposed target is `mu_success(X,R) = E[Q_b | A_b=1, X,R]`. Secondary resampling of successful scores addresses finite-primary-attempt Monte Carlo error in estimating this target. It does not establish sampling uncertainty over new original datasets or latent recovery uncertainty.

The packet prescribes a successful-fit conditional support point estimate and interval; it does not by those words alone prove that this particular conditional Monte Carlo interpretation is sufficient for every scientific uncertainty claim. Explicitly retain that distinction in the method card and statistical acceptance record.

If attempts are independent draws from one fixed procedure conditional on X,R, and success depends only on each attempt and its isolated randomness, then conditioning on a fixed success pattern preserves independence of the successful scores under the success-conditional law. Selection on score can change that law and its mean without by itself invalidating this conditional target. A common fixed dataset/reference does not alone create a reason to reject conditional independence. Shared adaptive settings, cross-attempt mutable state, run-wide random state not conditioned on, changing failure predicates, selective reruns or resource-dependent stopping require separate examination.

The current engine uses a fixed attempt count, child random streams and records failures. It accepts an arbitrary evaluator callback, so its source alone cannot prove that a future integrated scientific evaluator has no mutable cross-attempt state. Verify that implementation when its identity-bound D06 path is complete. The present generic toy-score studies do not validate the complete fitter pipeline.

The arithmetic matches the chosen percentile-resampled-mean family. Percentile-bootstrap coverage remains approximate and assumption-dependent; the independent reproduction and observed undercoverage are recorded in the execution report. Keep the nominal 95% label distinct from a guaranteed 95% coverage statement. No method replacement, endpoint adjustment, sample-size threshold, or favorable-case selection is authorized by this review.

The score-dependent-failure example targets the successful-attempt mean 1/3, while its all-attempt mean is 0. Low coverage of 0 measures a different target. The shared-shift study's zero target integrates over the random shift; its result is not coverage conditional on a fixed realized shift. Preserve both distinctions, including in machine-readable summaries whose historical field names use `conditional_target` for the shared-shift scenario.

Required closure evidence: an explicit scientific acceptance/revision record for the target and finite-sample limitations; actual evaluator conditioning/state review; D12 integration; exact secondary seed derivation; and the designated pilot/bounded-revision freeze. Until then retain the D13 implementation as development-only.

General statistical references reviewed for this assessment:

- [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html), resample-statistic-percentile construction. This does not approve SciPy defaults or replace the team's nearest-rank arithmetic.
- [Geyer, Bootstrap Percentile](https://www.stat.umn.edu/geyer/f07/5601/examp/percent.html), assumptions and approximate coverage limitations. No alternative interval is adopted here.

## D14: Executable Contract Still Required

The existing development stream derives each attempt from `SeedSequence(base_seed).spawn(B)`, draws training/validation/test positions sequentially from that child's generator, then draws an evaluator seed. Its replay verifier checks that exact behavior. Split draws are not separately role-addressed: changing an earlier split size changes subsequent draws. A development replay pass does not establish the pending production namespace specification.

Before changing that behavior, provide a versioned contract covering:

1. The approved Branch B-owned root seed and exact allowed observable tier/dataset identifiers.
2. Canonical input encoding, integer ranges, fixed hash/PRNG algorithms and dependency version, with reference input/output vectors. Never use Python's process-dependent built-in hash.
3. Separate primary-bootstrap, secondary-bootstrap and any evaluator/selection streams; explicit train, validation and test roles where required by the approved contract.
4. Deterministic direct replay of one attempt, invariant to execution order and parallel scheduling; retention of original attempt identity during retries.
5. A documented common-random-number policy if geometry comparisons intentionally share draws. Accidental cross-tier or cross-role stream reuse must not substitute for that policy.
6. Recorded run identity, derivation version, source/checksums and all consumed seeds/draw provenance. Hidden labels and restricted seeds are excluded.

This checklist completes the PL specification review without selecting a new seed rule. The handoff's proposed master seed 36 remains unapproved as a production value.

For timeout and resources, the approval artifact must identify the timed operation (individual optimizer, D04 operation, complete fit or bootstrap attempt), wall-clock accounting including relevant setup/extraction, monotonic-clock behavior, nested deadlines, actual failure codes and diagnostics, reference hardware/threads, repeat/timing statistic, permitted observable size variables, and an executable scaling formula with measured justification. Keep deadline expiry distinct from iteration-cap nonconvergence, numerical errors and memory exhaustion.

The full experiment requires at least 100 primary bootstrap repetitions per dataset/primary geometry. A proposed B=500 clears that numerical floor only. It does not establish sufficient successes, interval precision or feasible runtime. R=10,000 secondary resamples does not replace the primary budget. Review the precision/resource evidence at the required gate before selecting B or the timeout. Existing D04 feasibility findings remain open; no extra unbounded worst-case benchmark was required to reproduce the D12-D14 arithmetic evidence.

## Handoff and Release Boundary

The actionable engineering handoff is now explicit: complete identity-bound D06 support integration, complete all D12 reliability/sensitivity predicates, document evaluator independence, finish the D14 namespace and timing contract, then present exact artifacts and evidence for the designated scientific freeze. Continuing these focused checks is permitted; repeated passing tests alone cannot close the statistical or pilot decisions.

Project Boundary: the actual contents of this review were checked for Branch B and public disclosure. They contain permitted observable-side protocol requirements, generic mathematics, reviewed public code references and generic synthetic evidence only. No restricted experimental sources, hidden conditions, restricted seeds, latent labels, true hierarchy, sealed results or restricted paths are included. The protocol packets are cited by title and section and are not copied into the repository. No collaborator notification, data exchange, calibration, locked-test execution, unblinding or website publication is authorized by this record.
