# Threshold and blind-selection preparation (Weeks 5–6)

Run `python governance/threshold_blind_preparation.py --mode trace|blind --record RECORD.json --output NEW_REPORT.json`.
Schemas are implementation conventions for review records, not replacements for the existing official artifacts.

trace requires exact-byte references for the frozen sets and every geometry × candidate fitter × null family row: calibration manifest, processing config, test-support output, within-dataset selection, failure accounting, threshold rule, both approvals and threshold registry. It verifies matrix completeness and individual counts bounded by the planned denominator. The precise successful/failed/indeterminate classification and denominator reconciliation must follow frozen scientific accounting in independent review; the checker does not invent it. Actual empirical 95th percentiles and the maximum over families must be checked against the frozen rule and actual official calibration output. This tool chooses or calculates no threshold.

blind verifies the supplied candidate and geometry matrix is complete, selection is one registered candidate, recorded input is observable_only, truth-keyed selection and recalibration are false, and activated values equal the selected precomputed values. Exact selection-rule, input-manifest, audit, separation-attestation, threshold-registry and configuration-registry bytes are required. It does not read those documents as scientific definitions, validate custodian signatures or independently verify that supplied matrices match their referenced registries. Those checks and actual approved selection provenance remain mandatory before handoff/processing. Dummy tests are never actual approvals.

## Prespecified output shells
CSV shells in ../week6_8/shells contain no result rows. Their fields follow Admin Packet sections Procedure Acceptance, Positive-Control Recovery Gate, Hierarchy-Detection Acceptance and Scientific-Claim Acceptance, pp.53–55. Protocol-specific geometry/cell/family identities, estimand, CI method, failure conventions, multiplicity, region/sensitivity and claim rules must be linked to exact approved freeze references before final templates are frozen. No new metric, numerical acceptance criterion or claim is selected here.

A spreadsheet/figure-ready bundle must be finalized after approved definitions arrive. Current CSV structures advance preparation but are not a completed approved table_shells.xlsx or figure_spec.yaml deliverable.
