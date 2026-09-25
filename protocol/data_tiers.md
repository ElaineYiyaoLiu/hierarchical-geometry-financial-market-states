# Data tiers

The project uses four data tiers so development can proceed without weakening the blind evaluation.

## Development

Development datasets may disclose generating identities, latent labels, and ground truth when those details are needed to debug the interface, verify metrics, test code, or profile runtime. Development results are not part of the final performance evaluation.

## Calibration

Calibration datasets may disclose the hierarchy-support class and, when needed, a broad family identifier. Full generating parameters, latent labels, true trees, and the identity of primary experimental conditions remain hidden.

## Blind validation

Blind-validation datasets are released as observable data without support classes, generator-family identities, latent labels, true trees, or hidden generating parameters. Branch B uses this tier for ground-truth-free selection of the Common Fitter and related pipeline choices.

## Locked test

Locked-test datasets are observable-only and are processed after the analysis rules and pipeline have been frozen. The locked pipeline is run once per dataset. Ground truth is released only after the required predictions, support decisions, diagnostics, and failures have been submitted and frozen.
