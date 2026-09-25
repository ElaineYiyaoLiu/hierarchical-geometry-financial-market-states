# Blinding and release

Branch B works from observable vectors and the metadata explicitly released for the current data tier. During blind validation and locked testing, Branch B does not receive simulator equations, latent labels or paths, the true hierarchy, hidden generating parameters, or condition identities.

Development and calibration datasets may disclose additional information as described in `data_tiers.md`. These datasets should be clearly identified and kept separate from blind-validation and locked-test material.

Before ground truth is released for a blind or locked dataset, Branch B submits its required outputs and any failures. The Project Lead records the freeze and checksums, confirms that the submission is complete, and then authorizes truth release.

Branch A should not use preliminary Branch B performance on blind-validation or locked-test datasets to revise the generator. Likewise, Branch B should not infer hidden conditions from filenames, directory structure, identifiers, row order, numerical precision, missingness patterns, compression, timestamps, or file size.
