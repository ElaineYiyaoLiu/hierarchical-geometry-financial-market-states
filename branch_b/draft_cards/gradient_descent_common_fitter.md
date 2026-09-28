# Draft Common Fitter Card — gradient_descent_ultrametric

Status: candidate; not selected and not frozen.

- Role: candidate Common Fitter for all registered primary geometries.
- Method family: gradient-descent ultrametric fitting.
- Input: project-level commonly normalized observable dissimilarity matrix.
- Selection: one Common Fitter will later be selected using the frozen geometry-neutral, ground-truth-free rule.
- Geometry-specific fitter selection: prohibited.
- Hidden tree-recovery information for fitter selection: prohibited.
- Exact objective: pending project-specific specification.
- Initialization: pending.
- Convergence tolerance / iteration limit: pending.
- Timeout: pilot-dependent quantity; not yet frozen.
- Random seed rule: pending Branch B implementation record.
- Tree extraction, ties, zero-length branches, and degenerate-tree handling: pending.
- Numerical failure conventions: must use the project failure registry plus any documented method-specific subcodes.
