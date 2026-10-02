from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from branch_b.failures import BranchBFailure, ConfigurationRequired, FailureCode
from branch_b.fitters.base import FitResult


@dataclass(frozen=True)
class GradientDescentFitterConfig:
    graph_rule: str = "complete_graph"
    optimizer: str = "AMSGrad"
    learning_rate: float = 0.01
    convergence_tolerance: float = 1e-8
    convergence_patience: int = 10
    max_iterations: int = 1000
    near_zero_weight_tolerance: float = 1e-12
    tie_rule: str = "unresolved_multifurcation"
    zero_branch_rule: str = "preserve_and_treat_unresolved_structurally"
    degenerate_tree_rule: str = "structural_invalidity_only"
    random_restarts: int = 0
    deterministic_primary: bool = True
    timeout_seconds: float | None = None


class GradientDescentUltrametricFitter:
    """Configured candidate based on Chierchia & Perret's gradient-descent framework.

    Scientific/project settings frozen by Branch B for this development candidate:
    complete graph, AMSGrad, lr=0.01, input-weight initialization, relative objective
    tolerance 1e-8 for 10 consecutive iterations, max 1000 iterations, and no random
    restarts. Timeout remains pilot-fixed and is intentionally unset here.

    The executable optimizer kernel still requires a Python 3.14-compatible
    automatic-differentiation implementation of the paper's Dasgupta soft-cardinal
    objective and min-max/subdominant-ultrametric operator.
    """

    fitter_id = "gradient_descent_ultrametric"
    objective_id = "dasgupta_soft_cardinal"
    optimizer_family = "AMSGrad"
    initialization_rule = "working_weights_equal_input_weights"

    def __init__(self, config: GradientDescentFitterConfig | None = None):
        self.config = config or GradientDescentFitterConfig()
        self._validate_config()

    def _validate_config(self) -> None:
        c = self.config
        if c.graph_rule != "complete_graph":
            raise ValueError("registered graph rule is complete_graph")
        if c.optimizer != "AMSGrad":
            raise ValueError("registered optimizer is AMSGrad")
        if not np.isfinite(c.learning_rate) or c.learning_rate <= 0:
            raise ValueError("learning_rate must be finite and positive")
        if not np.isfinite(c.convergence_tolerance) or c.convergence_tolerance <= 0:
            raise ValueError("convergence_tolerance must be finite and positive")
        if c.convergence_patience <= 0 or c.max_iterations <= 0:
            raise ValueError("convergence_patience and max_iterations must be positive")
        if not np.isfinite(c.near_zero_weight_tolerance) or c.near_zero_weight_tolerance <= 0:
            raise ValueError("near_zero_weight_tolerance must be finite and positive")
        if c.random_restarts != 0 or not c.deterministic_primary:
            raise ValueError("registered primary candidate uses deterministic execution with no random restarts")
        if c.timeout_seconds is not None and (not np.isfinite(c.timeout_seconds) or c.timeout_seconds <= 0):
            raise ValueError("timeout_seconds must be positive when pilot-fixed")

    def complete_graph_edges(self, dissimilarity: object) -> tuple[np.ndarray, np.ndarray]:
        """Return complete-graph endpoint pairs and corresponding normalized weights."""
        d = self.validate_normalized_input(dissimilarity)
        i, j = np.triu_indices(d.shape[0], k=1)
        edges = np.column_stack((i, j)).astype(int, copy=False)
        weights = d[i, j].copy()
        return edges, weights

    def convergence_reached(self, objective_history: list[float]) -> bool:
        """Apply the registered 10-consecutive-iteration relative-improvement rule."""
        needed = self.config.convergence_patience + 1
        if len(objective_history) < needed:
            return False
        recent = objective_history[-needed:]
        improvements = [
            self.relative_objective_improvement(previous, current)
            for previous, current in zip(recent[:-1], recent[1:], strict=True)
        ]
        return all(value < self.config.convergence_tolerance for value in improvements)

    def source_specification(self) -> dict:
        return {
            "method_source": "Chierchia & Perret (2019), Ultrametric Fitting by Gradient Descent",
            "objective": self.objective_id,
            "ultrametric_parameterization": "min-max subdominant ultrametric Phi_G",
            "initialization": self.initialization_rule,
            "optimizer_family": self.optimizer_family,
            "global_optimum_guarantee": False,
        }

    def project_specification(self) -> dict:
        return {
            "graph_rule": self.config.graph_rule,
            "optimizer": self.config.optimizer,
            "learning_rate": self.config.learning_rate,
            "convergence_rule": {
                "relative_objective_improvement_below": self.config.convergence_tolerance,
                "consecutive_iterations": self.config.convergence_patience,
            },
            "max_iterations": self.config.max_iterations,
            "near_zero_weight_tolerance": self.config.near_zero_weight_tolerance,
            "near_zero_weight_handling": "DEGENERATE_DISTANCE",
            "tie_rule": self.config.tie_rule,
            "zero_branch_rule": self.config.zero_branch_rule,
            "degenerate_tree_rule": self.config.degenerate_tree_rule,
            "random_restarts": self.config.random_restarts,
            "deterministic_primary": self.config.deterministic_primary,
            "timeout_seconds": self.config.timeout_seconds,
        }

    def validate_normalized_input(self, dissimilarity: object) -> np.ndarray:
        d = np.asarray(dissimilarity, dtype=float)
        if d.ndim != 2 or d.shape[0] != d.shape[1] or d.shape[0] < 2:
            raise BranchBFailure(FailureCode.INPUT_SCHEMA, "fitter input must be a square matrix")
        if not np.isfinite(d).all():
            raise BranchBFailure(FailureCode.NONFINITE_INPUT, "fitter input contains non-finite values")
        if np.any(d < 0) or not np.allclose(d, d.T, rtol=0.0, atol=1e-12):
            raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "fitter input must be symmetric and nonnegative")
        if not np.allclose(np.diag(d), 0.0, rtol=0.0, atol=1e-12):
            raise BranchBFailure(FailureCode.DEGENERATE_DISTANCE, "fitter input diagonal must be zero")

        tri = np.triu_indices(d.shape[0], k=1)
        if np.any(d[tri] <= self.config.near_zero_weight_tolerance):
            raise BranchBFailure(
                FailureCode.DEGENERATE_DISTANCE,
                "normalized off-diagonal weight is zero or below the registered reciprocal-weight tolerance",
            )
        return d

    @staticmethod
    def relative_objective_improvement(previous: float, current: float) -> float:
        if not np.isfinite(previous) or not np.isfinite(current):
            raise BranchBFailure(FailureCode.NUMERICAL_FIT, "objective became non-finite")
        numerical_floor = np.finfo(float).tiny
        return abs(previous - current) / max(abs(previous), numerical_floor)

    def fit(self, dissimilarity: object, *, random_seed: int | None = None) -> FitResult:
        self.validate_normalized_input(dissimilarity)
        raise ConfigurationRequired(
            "registered fitter settings are complete except pilot-fixed timeout, but the "
            "Python 3.14 executable Dasgupta/min-max optimizer kernel has not yet been "
            "implemented and validated against the approved source"
        )
