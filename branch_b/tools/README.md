# Branch B gate-evidence checker

This is a development-only administrative check, not a scientific gate, protocol validator, or approval mechanism. It does not inspect observable data, pilot results, calibration results, or restricted truth.

## Python 3.14 execution

From the repository root, with a verified Python 3.14 interpreter:

```sh
python -c 'import sys; assert sys.version_info[:2] == (3, 14), sys.version'
python -m unittest discover -s branch_b/tests -p 'test_gate_evidence.py' -v
python -m branch_b.tools.check_gate_evidence branch_b/tools/gate_evidence_template.json
```

The CI workflow `.github/workflows/branch_b_evidence_tests.yml` runs the isolated unit tests using Python 3.14. A committed workflow is not evidence that CI passed; verify the actual run logs and interpreter version.

## Evidence input

The template contains empty objects for every administrative stage. To document a reviewed item, add its exact requirement key and an object with `verified: true` and a nonempty `evidence_ref`, for example:

```json
{
  "gate_5a": {
    "bounded_revision_approved": {
      "verified": true,
      "evidence_ref": "approved-record-reference"
    }
  }
}
```

This is a **format illustration only**, not a claim that any such record exists. Do not populate assertions until the actual authorized evidence has been inspected. Do not include sensitive or blinded material in public references.

The output's `evidence_complete` means only that all expected assertions are present. `authorization` is always `NOT_GRANTED_BY_THIS_TOOL`. Real gate decisions remain with the protocol-designated approvers and controlling records.

## Limitations

The requirement keys are a practical administrative checklist derived from the schedule, not an exhaustive substitute for the controlling Branch B packet or approved freeze records. Never use this tool to release calibration seeds, start pilot/calibration/independent processing, or declare a gate passed. Preserve every unresolved or contradictory record for human review.
