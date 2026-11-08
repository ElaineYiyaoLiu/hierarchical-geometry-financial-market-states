# Week 9 objective/gradient golden-case specification (development only)

Status: analytic reference and test plan; not executable verification, complete Common Fitter certification, or a scientific freeze. Scope is Branch B observable-side, synthetic examples only. Requires actual Python 3.14 execution for test evidence.

## Approved mathematical inputs

For active distinct original identities I, integer multiplicities m_i>0, fixed positive admissible normalized dissimilarities Delta_ij (i<j), and complete graph G on I:

- W = sum_{i<j} m_i*m_j;
- sigma(z) = 1/(1+exp(-z)); sigmoid beta is fixed at 5;
- u=Phi_G(w) is the min-max/subdominant ultrametric obtained from direct nonnegative edge weights;
- S_i(h) = sum_{k in I} m_k*sigma(5*(h-u_ik)), with u_ii=0;
- J(u;Delta,m) = (1/W) * sum_{i<j} m_i*m_j*[S_i(u_ij)+S_j(u_ij)]/(2*Delta_ij).

Self-mass is included in S_i, but same-original-identity outer reciprocal edges are absent. When all m_i=1, J reduces to the approved ordinary D01 formula; no separate cluster-size regularization is included. Required input reciprocal denominators are fixed Delta_ij, never u_ij.

## Analytic derivative with respect to symmetric off-diagonal u

Let D_ab(p,q) = 1 if p!=q and the unordered pair {p,q} equals {a,b}; otherwise 0. Diagonal u_ii=0 is constant, not an independent coordinate. Define sigma_prime(z)=sigma(z)*(1-sigma(z)).

For each a<b:

    H_ab = (5/(2*W)) *
        sum_{i<j} (m_i*m_j/Delta_ij) *
        sum_k m_k * (
           sigma_prime(5*(u_ij-u_ik))*(D_ab(i,j)-D_ab(i,k))
         + sigma_prime(5*(u_ij-u_jk))*(D_ab(i,j)-D_ab(j,k))
        ).

H is the derivative of the smooth scalar J with respect to the independent unordered off-diagonal entries u_ab. It does not itself assume unconstrained independent ultrametric entries: the composite derivative through Phi_G still requires the min-max Jacobian.

For each admissible strict edge ordering pi, let P_pi denote the limiting Jacobian of Phi_G, so g_pi=P_pi^T H. The approved D04 rule groups strict orderings by their distinct realizable rooted hierarchy T, takes an equal conditional average of g_pi within each T, then weights each T equally. Because H is continuous in u for this specified sigmoid objective, H is common to the limits at a fixed tied w. Thus computing the approved average of P_pi and multiplying by H gives the same gradient as averaging the full limiting gradients. This algebraic simplification does not establish an efficient exact algorithm for the average.

## Hand-derived golden cases (not executed)

### Case G1: two distinct vertices, ordinary or multiplicity weighted

Input: I={A,B}, m_A=p, m_B=q, p,q positive integers, Delta_AB=d>0, w_AB=x>=0. W=pq, u_AB=x.

    S_A(x)=p*sigma(5*x)+q/2
    S_B(x)=q*sigma(5*x)+p/2
    J(x)=(p+q)/(2*d) * [sigma(5*x)+1/2]
    dJ/dx=5*(p+q)/(2*d) * sigma_prime(5*x).

For p=q=1: J(x)=[sigma(5*x)+1/2]/d.
For p=2,q=3: J(x)=5*[sigma(5*x)+1/2]/(2*d).
At x=0, sigma(0)=1/2 and sigma_prime(0)=1/4; use one-sided feasible differentiation when evaluating the boundary. There is no duplicate-generated AB diagonal edge.

### Case G2: tie-free three-vertex min-max transform

Input: graph edges AB=a, AC=b, BC=c with 0<a<b<c and fixed positive Delta_AB,Delta_AC,Delta_BC. The unique minimum spanning tree edges are AB and AC, and the output distances are u_AB=a, u_AC=b, u_BC=b. In coordinates [AB,AC,BC] for both output and working edges, the Jacobian at strict a<b<c is

    P = [[1,0,0],
         [0,1,0],
         [0,1,0]].

Thus, for the smooth objective gradient H=[H_AB,H_AC,H_BC], the working gradient is [H_AB,H_AC+H_BC,0]. Compare against feasible finite differences that do not cross strict edge-order boundaries.

### Case G3: three-vertex all-edge tie, one output coordinate

Input: w_AB=w_AC=w_BC=x>=0, complete graph, evaluate only Phi_G(w)_AB. There are six strict orders and three distinct rooted binary hierarchies (AB-first, AC-first, BC-first). For the approved tree-equal, within-tree order-equal convention, the limiting Jacobian row for this output averages to

    [2/3, 1/6, 1/6] in working edge order [AB,AC,BC].

This is a test of a single min-max output component only; to certify the full D04 gradient, average all output rows and multiply by the full H computed above. Do not substitute a hard tree-dependent cluster area for the approved smooth objective.

### Case G4: absence and multiplicity

A draw with original occurrence counts (m_A,m_B,m_C,m_D)=(2,3,1,0) has active vertices A,B,C and pair weights q_AB=6, q_AC=2, q_BC=3, W=11. There is no graph vertex D, no AA/BB/CC reciprocal denominator, and each S_i includes masses (2,3,1) across A,B,C. The original ID mapping and raw draw counts must remain available as provenance.

## Required tests under Python 3.14

1. Evaluate G1 closed forms at a predetermined set of nonboundary and boundary values. Independently compare the differentiable interior gradient against centered finite differences. At x=0 use a feasible one-sided difference.
2. Verify G2 min-max matrix/Jacobian exactly and differentiate the full J in the interior of the edge-order chamber.
3. Exhaustively enumerate strict ordering possibilities for G3; compare hierarchy-conditioned gradient averages against the stated single-row result and validate relabeling equivariance.
4. Verify G4 multiplicity weights and self-mass exactly; test reduction to D01 when m_i=1.
5. Test immutable input Delta denominators, including permitted degeneracy behavior for *distinct* identities with zero/near-zero Delta, and independence from optimized zero u edges.
6. For larger tied components, investigate an exact dynamic-programming/counting method. If unavailable, continue exact enumeration with deadline checks until the approved TIMEOUT deadline is reached. Never treat predicted infeasibility as an immediate TIMEOUT or substitute sampled approximation.
7. Check identity binding and failure accounting through bootstrap/preprocessing/geometry/fitter, without silently assuming deduplication equals repeated-row estimation. Compare explicit repeated-row estimators with weighted-distinct-row versions before replacing any stage.
8. Record actual Python 3.14 interpreter/dependency versions, source commit, deterministic test configurations, diagnostics, failures and checksums. No results from another Python version may count as scientific or golden evidence.

## Known gaps and nonclaims

- Exact source-implementation soft-area/sigmoid conformance has not been certified.
- Small-case algebra does not prove optimizer correctness, convergence, or D04 dynamic-programming feasibility.
- The low-distinct-observation failure/reliability rule and the pilot-frozen timeout value remain open.
- The source as inspected on 2026-11-08 includes a `ConfigurationRequired` fitter stub and an unchecked duplicate-bootstrap/reciprocal-weight conflict. This document does not fix code.
- The environment used for this documentation step lacks Python 3.14; an attempted `uv python install 3.14` failed due to DNS resolution. No project scientific code or test was executed.
