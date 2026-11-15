# D11 — single Common Fitter, Branch B team selection (2026-11-15)

**Team confirmation:** Branch B will register **exactly one** candidate Common Fitter: the existing gradient-descent min-max ultrametric fitter with the recorded D01–D06 development method choices. The team has explicitly confirmed there are no competing Common-Fitter candidates to rank.

**Status:** Branch B team-approved selection direction, **not** a project-level method freeze, complete Common Fitter Card approval, implementation certification, pilot authorization or scientific-data processing permission.

## Executable selection rule for the one-candidate registry

- Candidate registry cardinality: exactly one.
- If that sole registered candidate satisfies all independently required eligibility and conformance checks, select it for every registered primary geometry with the same prespecified configuration.
- If it is ineligible, missing, fails a mandatory gate, or cannot be certified, **do not** silently select or create a fallback fitter; the applicable workflow remains blocked or reports the failure/indeterminate outcome required by its governing protocol.
- No competitive lexicographic ranking, rank aggregation across geometries, or tie-break ordering among fitters is applicable to a one-candidate registry.
- Validation-only geometry-parameter selection, hierarchy-support calibration, bootstrap reliability and all other protocol-defined validation/failure rules remain in force. They are not waived by D11.

## Relationship to historical D11 proposal

The October 20 intake had recorded a proposed lexicographic failure / distortion / stability / resource comparison of multiple fitters. That comparison is **not applicable** given the team-confirmed one-candidate registry and is superseded as the proposed D11 workflow. It may not be revived without a separately authorized revision to the candidate registry and selection method.

The draft Common Fitter Card is currently labeled candidate/not selected, and the production `GradientDescentUltrametricFitter.fit` remains fail-closed. Those artifacts are not changed by this note. Development tests and team selection do not automatically constitute complete card freeze or source-conformance certification.

## Remaining gates

1. Project Lead confirmation that the one-candidate selection and no-comparison interpretation meets the controlling protocol's Common-Fitter selection requirement.
2. Final source-conformance review, reconciliation of registered historical D05 defaults, complete D06 integration, and approved numerical/tree/failure conventions.
3. Actual Python 3.14 environment/JUnit/reproducibility review and required card/selection freeze entries before their scientific gates.
4. Pilot-only processing when explicitly authorized; no locked-test or unblinding action is authorized.

D07, D08 and D15 remain separately approved at Branch B team-proposal level; D13's interval method remains pending.

**Public-write safety verification:** Actual content contains only Branch B-visible candidate-method specification, user-confirmed team selection and public governance status. It contains no generator implementation, restricted parameters or experimental conditions, generator-owned seeds, latent labels, true hierarchy, sealed truth, or side-channel inference; safe for the public shared review branch.
