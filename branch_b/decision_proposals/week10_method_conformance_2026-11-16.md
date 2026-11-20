# Week 10 Method Conformance Review

Reviewed November 16, 2026. Project source: `ef9e8515e3c4cfc98d4cc0f6b40dfdfa5c128225`, whose scientific implementation is unchanged from the submitted `74954ae5126e5967e700234a8ccd8d5379a8e9f6`. This is a completed source/documentary review and engineering handoff. It is not a formal scientific approval or production activation.

## Sources and Interpretation

The Version 2 Branch B Packet controls project requirements. The November 8 candidate decisions and November 15 team records determine the reviewed development choices. The paper supplies a methodological reference; the project is not a claim of bitwise equivalence to the authors' software.

The paper was retrieved as arXiv `1905.10566v3`. The authors' implementation was inspected at commit `6c233e2842af3c1e56b989059fa503091f646a31`: `ultrametric/optimization.py` and `ultrametric/loss.py`. Exact retrieved-file hashes are in the closeout evidence. The authors' PyTorch/Higra stack was not executed in this review.

| Component | Source / selected project behavior | Inspected implementation | Finding |
| --- | --- | --- | --- |
| Objective | Paper Eq. 12 uses fixed input dissimilarity denominators. Project D01 specifies endpoint average and edge/mass normalization. | `fitters/d01_d06_objective.py`: fixed Delta; endpoint factor 1/2; W=sum m_i*m_j | Matches the recorded project formula. With unit masses, W is the complete-graph edge count. Paper Algorithm 5's printed denominator discrepancy remains an explicitly resolved project choice, not proof all paper pseudocode is identical. |
| Soft cardinality | Project beta=5 and mass-weighted endpoint sums including self terms | Same function: sigmoid(5*(u_ij-u_ik)); weighted by m_k | Matches the recorded candidate. No new beta search or penalty is introduced. |
| Initialization | Paper Algorithm 1 starts at input weights; authors' default software starts at their subdominant transform | `development_optimizer.py` copies Delta into working weights | Matches the project/paper choice; differs deliberately from the authors' default software path. |
| Positivity | Project directly projects updated weights onto the nonnegative orthant | `d03_amsgrad.py`: raw moment updates, bias correction, unmasked gradient, then max(0,candidate) | Matches the recorded candidate arithmetic. Authors' default applies softplus in its criterion; that is a different parameterization. |
| AMSGrad | Project constants 0.01, 0.9, 0.999, 1e-8 and raw-second-moment maximum before bias correction | `d03_amsgrad.py` and optimizer update order | Source arithmetic is explicit; existing component tests passed. This is not a blanket certificate against every PyTorch version. |
| Tied derivatives | D04 hierarchy-balanced average of strict-order limiting Jacobians; exact equal working weights only | `exact_tie_dp.py`, `d04_gradient_adapter.py` | The recurrence preserves the selected average; proof below. Small-oracle tests pass. Practical large-tie feasibility remains open. |
| Stopping | D05 relative change <1e-6 for five complete updates, max 1,000, recorded initial-objective floor formula | `d05_stopping.py`, `development_optimizer.py` | Development path matches recorded arithmetic. Historical production configuration still exposes 1e-8/10 and must be reconciled before activation. |
| Multiplicity | Distinct original identities, product pair mass, soft mass, no same-ID reciprocal edges | Objective, D06 development fitter and split adapters | Development components exist. The legacy checked bootstrap remains occurrence-labeled and is not the certified D06 scientific entry point. |
| Numerical input | D07 team proposal validates, then symmetrically averages accepted input and sets diagonal to zero | `development_d06_fitter.py` still extracts the original upper triangle after historical validation | Selected canonicalization is not demonstrated in this entry point. Integration revision remains necessary. |
| Tree and failure export | Approved numeric/tree comparison and registered failure meanings required | Development tree extraction/reconstruction; diagnostics sidecar | Exact synthetic reconstruction is not a universal floating-point rule. Complete the output-height and failure-code contract before certification. |

Paths in this table are relative to `branch_b/`.

## D04 Recurrence Check

At a tied weight level, a state records its processed-edge mask and complete labeled rooted forest. Those determine every available next edge, whether its merge is redundant, the resulting forest, and the Jacobian increment. Earlier path details do not change these transitions.

Suppose a state represents c prefixes and their summed Jacobian A. Extending all prefixes by one permitted edge with increment E produces c extensions and sum A+cE. The implementation adds exactly these quantities. When multiple states reach the same next mask/forest it adds their counts and sums. Induction on processed edges therefore preserves the exact strict-order multiset and its accumulated derivative. A level is exhausted before processing the next exact weight, so unequal levels are never permuted.

At the final connected labeled tree H, let c_H be its strict-order count and A_H its sum. The selected project average is `(1/number_of_H) * sum_H A_H/c_H`. The implementation uses the denominator `c_H * number_of_H` for each final state. It therefore gives equal weight to distinct realizable full hierarchies and averages within each hierarchy, rather than weighting hierarchies by how many orders produce them. Rational accumulation preserves this combinatorial averaging exactly.

This argument concerns the registered complete graph and selected project measure. It does not establish feasible runtime on the full scientific bank, change that measure, justify an approximate fallback, or approve a new complexity cutoff.

## D07 Closure Text

Retain the team-selected candidate: reject invalid input first; symmetrically average only accepted off-diagonal entries; set the computational diagonal to zero; then test the existing reciprocal-denominator predicate on those computational entries. The final card must specify placement relative to the native geometry/common normalization and bind the objective, diagnostics and export to the same intended matrix.

Keep four separate definitions: input validity tolerance, reciprocal-denominator admissibility, D04 exact working-edge ties, and output-tree height/grouping/reconstruction. Pairwise height closeness is not transitive. Heights 0, 0.75*tau and 1.5*tau demonstrate why the predicate alone does not define unique groups. A deterministic grouping convention requires a separate explicit decision; this review selects none.

Boundary and invariance evidence must cover below/equal/above tolerance, transposition, joint relabeling, canonical denominator boundaries, preservation of exact D04 ties, and matrix/tree agreement under the eventual approved convention. Existing large-deviation invalid schema fixtures do not establish every floating-point boundary.

## Certification Disposition

The available development arithmetic is consistent with the recorded project choices within the inspected scope. Complete D07/D06 integration, D05 configuration reconciliation, numeric tree semantics, failure export and practical exact-D04 feasibility before scientific fitter certification. A one-candidate registry does not remove these requirements. The official fitter remains fail-closed.

Project Boundary: actual text was reviewed for Branch B/public disclosure. It contains public methodological comparisons, permitted candidate specifications, general mathematics and engineering findings. No restricted experimental material or approval status was introduced.

Sources: [paper v3](https://arxiv.org/abs/1905.10566v3), [pinned authors' software](https://github.com/PerretB/ultrametric-fitting/tree/6c233e2842af3c1e56b989059fa503091f646a31), [existing D12–D14 disposition](d12_d14_pl_disposition_2026-11-15.md).
