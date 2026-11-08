# Draft Common Fitter Card — gradient_descent_ultrametric

Status: candidate; not selected; project-specific development settings approved; not frozen for pilot exchange.

## Source and role

- Fitter identifier: `gradient_descent_ultrametric`
- Source: Chierchia & Perret, *Ultrametric Fitting by Gradient Descent* (NeurIPS 2019 / arXiv:1905.10566v3).
- Registered objective: Dasgupta soft-cardinal relaxation.
- Ultrametric parameterization: min-max/subdominant-ultrametric operator.
- Initialization: working edge weights equal the input edge weights.
- Common application: the same fitter configuration applies to every registered primary geometry.

## D01 objective decision (2026-11-08; approved direction, not complete fitter freeze)

Branch B approves retaining the registered **Dasgupta-only soft-cardinality relaxation**. No separate cluster-size penalty or nonzero cluster-size lambda term is added to this candidate. This is a method choice, not an inference from scientific performance.

For ordinary, unweighted observations with the complete undirected edge set E={(i,j): i<j}, M=|E|, commonly normalized fixed input dissimilarity Delta, working weights w>=0, and u=Phi_G(w), the approved baseline structure is:

    J_D01(w; Delta, beta) =
        (1/M) * sum_{i<j} [S_i(u_ij;u,beta) + S_j(u_ij;u,beta)] / (2*Delta_ij).

The reciprocal denominator is the **fixed input** Delta_ij (never the fitted u_ij); soft cardinalities are symmetrically averaged across endpoints; contributions are averaged over undirected edges. The existing input admissibility/near-zero-denominator convention remains in force pending D06 reconciliation. No additional regularization is implied by the source paper's discussion of other objectives.

The D02 beta and D06 multiplicity/self-mass decisions are separately recorded below. Source-level sigmoid conformance, any remaining numerical/zero-distance admissibility details, full-pipeline equivalence, and the complete D04 tied-gradient derivation remain open. Do not silently fix these implementation dependencies from this baseline formula. The registered candidate is not selected or frozen, and the complete Python 3.14 scientific fitter remains unimplemented.

## D02 sigmoid beta decision (2026-11-08)

- Branch B team-selected and fixed soft-cardinality sigmoid parameter: **beta = 5**.
- This is the candidate's fixed method parameter, not a calibration search starting point. Do not manually retune beta using development, pilot, hierarchy-support calibration, blind-validation, independent-null, or locked-test performance without an authorized protocol revision.
- The team decision is frozen for this candidate's development specification. The full Common Fitter Card, implementation, and applicable project-level freeze gate remain pending; this record does not claim that the complete fitter is formally frozen or selected.
- Exact sigmoid/self-contribution and bootstrap soft-mass implementation details remain open and require consistency with beta = 5.

## D06 bootstrap multiplicity decision (2026-11-08; approved method direction, not complete fitter freeze)

For each bootstrap draw, retain the canonical original sample identities and integer occurrence multiplicities m_i >= 0. The active set I_b = {i : m_i > 0} contains one graph vertex and one output leaf per distinct original identity; repeated occurrences do not become new original leaves. Preserve the full draw mapping, counts, attempt and failure records for provenance.

Construct the fitted complete undirected graph on I_b, with one edge (i,j) for i<j, and use the approved product pair weights q_ij = m_i * m_j. Use the approved fixed-beta sigmoid sigma(z) = 1/(1+exp(-z)) at beta=5. The multiplicity-weighted soft mass is

    S_i^b(h;u,m) = sum_{k in I_b} m_k * sigma(5*(h-u_ik))

including the k=i self-mass contribution m_i*sigma(5*h), with u_ii=0. This is a smooth self-contribution, not a forced full mass. The *outer* reciprocal-weight Dasgupta edge sum includes only distinct identities i<j; no diagonal or same-original-identity edge is created.

With fixed commonly normalized bootstrap input Delta_ij for distinct active identities, u=Phi_{G_b}(w), and W_b = sum_{i<j in I_b} m_i*m_j, the approved bootstrap weighted-mean objective is

    J_b(w;Delta,m) =
      (1/W_b) * sum_{i<j in I_b}
      (m_i*m_j) * [S_i^b(u_ij;u,m)+S_j^b(u_ij;u,m)] / (2*Delta_ij).

When all active multiplicities equal one, this reduces to D01 on that active vertex set. W_b must be positive for the formula to apply; minimum distinct-observation reliability and precise unsuccessful-fit mapping are still governed by separately specified protocol/failure rules. Do not invent a code here.

Duplicate-induced within-identity zero distances do not create reciprocal denominators. For *distinct* original identities, the existing input admissibility/near-zero-distance convention remains applicable, including DEGENERATE_DISTANCE where currently prescribed; do not floor, jitter or silently remove a distinct pair. Zero *optimized* ultrametric edges are not zero input denominators.

Full-pipeline fidelity: repeated bootstrap occurrences must retain their frequency effects in any train-estimated preprocessing, geometry transformation, selection and fitting stages to which the frozen bootstrap pipeline applies. If a distinct-row weighted representation replaces repeated-row computations upstream of the fitter, demonstrate exact equivalence for each affected algorithm or obtain separate authorization. The current checked pipeline still feeds repeated rows and has not been scientifically adapted to this D06 method; this decision does not assert integration success.

Outstanding mathematical/engineering work: verify the exact source-backed sigmoid/soft-area convention for the adopted D01 objective; derive and test the ordinary and multiplicity-weighted full-objective gradients including D04 ties; establish W_b=0 and low-distinct-count outcomes under approved reliability/failure rules; reconcile distinct-pair normalized dissimilarities with the complete bootstrap preprocessing/geometry pipeline; implement the approved identity/mass interface; and validate under actual Python 3.14 with synthetic golden cases. No full Common Fitter selection, implementation certification, pilot freeze, or locked-test authorization is asserted.

## Input and graph

- Input: the commonly normalized pairwise dissimilarity matrix.
- Graph rule: complete graph over all observations, with one edge for every pair `i < j`.
- Common normalization: divide the native dissimilarity matrix by its maximum finite off-diagonal entry.
- Normalization degeneracy: if the maximum off-diagonal native dissimilarity is `<= 1e-12`, return `DEGENERATE_DISTANCE`.

## Optimizer and stopping

Approved D03 and D05 decisions (2026-11-08; candidate settings, not final Common Fitter freeze):

- Working weights initialized to fixed input edge weights; AMSGrad moments initialized to zero.
- Direct nonnegative working weights, projected after each *complete* optimizer update; do not artificially zero gradients on boundary weights.
- Bias-corrected AMSGrad, beta1=0.9, beta2=0.999, epsilon=1e-8, learning rate=0.01; no random restarts.
- Compute the finite objective after each complete projected update. Relative change at iteration t:
  r_t = abs(J_t - J_(t-1)) / max(abs(J_(t-1)), abs(J_0), 1e-12).
- Converged after 5 consecutive completed updates with r_t < 1e-6; reset the consecutive counter otherwise.
- Maximum 1000 completed optimizer updates. A cap reached without convergence is NUMERICAL_FIT with distinct iteration-cap/nonconvergence diagnostic; runtime deadline expiry is TIMEOUT. Keep numerical calculation errors under NUMERICAL_FIT with distinct diagnostics, subject to failure-code registry reconciliation.
- Retain objective/relative-change history, iterations, elapsed time, convergence status and failure diagnostics. Timeout duration remains pilot-dependent.
- D04 exact tie-averaged gradient remains mathematically and computationally unverified; approximate averaging is not approved.
- Global optimum guarantee: none.

Historical development code in `branch_b/fitters/gradient_descent.py` still contains the superseded 1e-8/10-iteration settings and `ConfigurationRequired` stub; it must be reconciled and verified under actual Python 3.14 before any scientific execution. Do not claim that this card update changes executable behavior.

## Reciprocal-weight safety

The Dasgupta objective uses reciprocal input weights.

- Registered normalized near-zero tolerance: `1e-12`.
- If any required normalized off-diagonal weight is `<= 1e-12`, return `DEGENERATE_DISTANCE`.
- Do not silently floor or regularize the denominator.

## Tree extraction conventions

- Equal-height ties: preserve as unresolved multifurcations; do not arbitrarily binary-resolve them.
- Zero-length branches: preserve branch length 0 and treat the associated relation as unresolved for rooted-topology comparisons.
- `DEGENERATE_TREE`: reserve for structural invalidity (for example cycle, disconnected node, multiple parents, missing root, invalid leaf set, or an optimizer output that cannot be represented as a valid rooted tree).
- Multifurcations, ties, zero-length branches, and a fully unresolved but structurally valid star are not by themselves `DEGENERATE_TREE`.

## Randomness and reproducibility

- Primary candidate execution is deterministic where the dependency stack permits deterministic behavior.
- No random restarts.
- Record a Branch B-owned run seed field for provenance even when the optimizer consumes no stochastic randomness.
- Generator-owned or hidden seeds are prohibited.

## Timeout

Timeout remains pilot-dependent under the controlling protocol and is not numerically fixed here. A pilot-fixed timeout failure must be recorded as `TIMEOUT`.

## Remaining implementation item

The source-conformance review in `branch_b/decision_proposals/common_fitter_source_conformance_2026-10-02.md` documents differences between paper Algorithm 1 and the authors' software defaults. Subsequent team decisions select input-weight initialization, direct nonnegative weights with projection, and fixed sigmoid beta=5. The exact source-to-method sigmoid/soft-area expression must still be verified, as must the D01/D06 objective and D04 tie-gradient under actual Python 3.14; an executable scientific kernel and golden test evidence do not yet exist.

The final Common-Fitter selection remains geometry-neutral, ground-truth-free, and subject to its later protocol freeze.
