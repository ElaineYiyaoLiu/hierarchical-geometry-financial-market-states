# Week 4 audit preparation

Status: PREPARATION ONLY. Pilot exchange and formal generation remain BLOCKED.

Sources: Version 2 Admin Packet Appendices G.1, G.4, J and K; Version 2 Branch B Packet Appendix J; Schedule Week 4/5. Protocol requirements are controlling. CSV/JSON formats and reference fields are implementation choices; they do not approve scientific values.

`appendix_j_evidence_matrix.csv` maps every J.1-J.18 criterion to owner, artifact, access route and approval fields. All pilot-exit rows begin PENDING. A completed template or successful computation does not pass the gate.

Required sequence: initial five attempts per sentinel; frozen initial outputs; custodian sealed binary check; if triggered, uniform expansion to ten; frozen supplemental outputs; signed permitted resource/precision release; PL and Faculty pilot exit. Terminal generator/fit failures remain in denominators and manifests. No targeted expansion or performance-driven condition replacement.

PL sees observable/interface integrity, permitted numerical diagnostics, aggregate runtime/storage/throughput, approved signed fields and restricted-side attestations. Detailed truth-keyed recovery, condition mappings and seeds remain sealed. Exact trigger and field allowlist require approval/freeze before associated inspection; the present precision plan does not provide them.

Use `python governance/week4/validate_pilot_exit.py --matrix governance/week4/appendix_j_evidence_matrix.csv --evidence-root .`. PENDING rows produce BLOCKED. Validated evidence and signatures must be reviewed by the approving authority; the script never grants generation, exchange, calibration or locked-test authorization.

## A and PL evidence closure

```
python governance/prepare_a_pl_queue.py --output a_pl_closure_queue.json
python governance/check_minimum_effect_provenance.py --record governance/minimum_effect_provenance.template.json --output minimum_effect_consistency.json
```

The queue prioritizes eight A/PL/custodian work items from the existing complete gate audit. It changes no B or Faculty row and grants no approval. The provenance checker verifies evidence checksums and strict UTC ordering of the recorded freeze and earliest relevant inspection. It ignores self-declared chronology flags. REVIEWABLE means that the supplied records are consistent; signatures, authority, original decision contents and inspection completeness still require review. Missing original records retain BLOCKED.

The existing audit requires `approval_sha256` whenever an `approval_ref` is supplied. Record it only from the actual approval file. A checksum field does not populate or execute an approval.
