from __future__ import annotations

from dataclasses import dataclass

from branch_b.failures import ConfigurationRequired
from branch_b.fitters.base import FitResult


@dataclass(frozen=True)
class GradientDescentFitterConfig:
    graph_rule: str | None = None
    learning_rate: float | None = None
    convergence_tolerance: float | None = None
    max_iterations: int | None = None
    near_zero_weight_tolerance: float | None = None
    tie_rule: str | None = None
    zero_branch_rule: str | None = None
    degenerate_tree_rule: str | None = None
    timeout_seconds: float | None = None


class GradientDescentUltrametricFitter:
    """Candidate based on Chierchia & Perret's gradient-descent framework.

    Source-backed details:
    - Dasgupta objective with differentiable soft cardinality
    - min-max/subdominant-ultrametric parameterization
    - initialization from input edge weights
    - AMSGrad optimizer family

    Project-specific settings not uniquely fixed by the paper remain required.
    """

    fitter_id = "gradient_descent_ultrametric"
    objective_id = "dasgupta_soft_cardinal"
    optimizer_family = "AMSGrad"
    initialization_rule = "working_weights_equal_input_weights"

    def __init__(self, config: GradientDescentFitterConfig | None = None):
        self.config = config or GradientDescentFitterConfig()

    def source_specification(self) -> dict:
        return {
            "method_source": "Chierchia & Perret (2019), Ultrametric Fitting by Gradient Descent",
            "objective": self.objective_id,
            "ultrametric_parameterization": "min-max subdominant ultrametric Phi_G",
            "initialization": self.initialization_rule,
            "optimizer_family": self.optimizer_family,
            "paper_learning_rates_reported": [0.01, 0.1],
            "paper_convergence_note": "usually reached in a little over 100 iterations in framework validation",
            "global_optimum_guarantee": False,
        }

    def unresolved_configuration(self) -> list[str]:
        required = {
            "graph_rule": self.config.graph_rule,
            "learning_rate": self.config.learning_rate,
            "convergence_tolerance": self.config.convergence_tolerance,
            "max_iterations": self.config.max_iterations,
            "near_zero_weight_tolerance": self.config.near_zero_weight_tolerance,
            "tie_rule": self.config.tie_rule,
            "zero_branch_rule": self.config.zero_branch_rule,
            "degenerate_tree_rule": self.config.degenerate_tree_rule,
        }
        return [name for name, value in required.items() if value is None]

    def fit(self, dissimilarity: object, *, random_seed: int | None = None) -> FitResult:
        missing = self.unresolved_configuration()
        if missing:
            raise ConfigurationRequired(
                "gradient-descent Common Fitter project configuration is incomplete: "
                + ", ".join(missing)
            )
        raise ConfigurationRequired(
            "source-backed fitter specification is recorded, but executable optimization "
            "must not run until remaining project-specific settings and Python 3.14 "
            "dependencies are frozen and implemented"
        )
