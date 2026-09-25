# Hierarchical Geometry of Financial Market States

This project studies whether hierarchical structure in synthetic financial market states can be recovered more effectively with valuation-based geometry than with standard continuous geometries.

The study uses a blinded two-branch design. Branch A generates synthetic datasets and holds restricted generating information and ground truth. Branch B works from observable data and develops the recovery pipeline.

## Repository layout

- `protocol/` — shared protocol and blinding rules
- `interface_package/` — observable-data and output contracts
- `validator/` — interface validation
- `golden_cases/` — small validation examples
- `governance/` — shared naming, checksum, access, and freeze records
- `branch_b/` — Branch B working area

## Project boundary

Branch A generator code, restricted configurations, seeds, latent labels, true hierarchy, and sealed ground truth are maintained separately in a private synthetic-generator repository.
