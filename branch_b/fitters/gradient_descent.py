from __future__ import annotations

from branch_b.failures import ConfigurationRequired
from branch_b.fitters.base import FitResult


class GradientDescentUltrametricFitter:
    """Registered candidate Common Fitter.

    The source record selects the gradient-descent ultrametric-fitting family as a
    candidate, but the project-specific objective, initialization, stopping rule,
    and related numerical conventions are not yet fully specified. This class
    therefore exists as an integration interface and fails closed until its card
    is completed and approved.
    """

    fitter_id = "gradient_descent_ultrametric"

    def fit(self, dissimilarity: object, *, random_seed: int | None = None) -> FitResult:
        raise ConfigurationRequired(
            "gradient-descent Common Fitter card is incomplete: objective, initialization, "
            "stopping rule, and failure conventions must be frozen before execution"
        )
