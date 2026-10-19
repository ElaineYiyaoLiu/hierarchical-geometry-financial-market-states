# Branch B

Branch B develops the observable-data side of the study: preprocessing, candidate geometries, the common fitting pipeline, hierarchy-support analysis, uncertainty estimates, and output formatting.

## Current checkpoint

The [observable-to-output validation report](output_transport_validation_2026-10-19.md) is the current development handoff. It records the checked input loader, outgoing schema/provenance transport, inventory accounting, actual Python 3.14.8 results, retained failures, and the remaining scientific decision boundary. The concrete integration repairs identified by the [audit](integration_audit_2026-10-19.md) and [checked-pipeline follow-up](checked_integration_validation_2026-10-19.md) are implemented within their stated scopes; the scientific optimizer, numerical conventions, and duplicate-bootstrap weighting reconciliation remain unresolved.

Use the [checked transport guide](output/checked_transport.md) and [checked pipeline guide](recovery_pipeline/checked_integration.md) for the interfaces. Generic development entry points are not scientific certificates. The [Weeks 1-6 evidence checklist](weeks_1_to_6_evidence_checklist.md) retains its earlier dated reconciliation; the audit and newer reports qualify that earlier stopping assessment and supply later execution evidence.

The [reviewed packaging snapshot](packaging_source_snapshot_validation_2026-10-19.md) remains a pinned four-file packaging-component artifact, not the scientific validation runner or an archive of the newer modules. Passing development tests does not approve methods, complete end-to-end scientific golden testing, or authorize bank processing.

## Data boundary

Before authorized truth release, all stages, including development and pilot work, use only permitted observable information and explicitly approved disclosures. Generator equations, latent labels, true hierarchies, hidden condition parameters, and other restricted Branch A material remain unavailable until the applicable release authorization.

Method definitions and fitted-pipeline choices should be versioned before they are frozen for later stages. Existing scientific settings are not changed by the evidence handoff, and pending decisions must not be filled with implementation defaults.

## Week 1 setup records

- `geometry_registry.md` - proposed observable geometries and candidate Common Fitter
- `draft_cards/` - draft, explicitly non-frozen method cards
- `branch_b_environment.txt` - historical setup environment and links to later development evidence
- `seed_namespace_b.yaml` - Branch B-owned stochastic namespace policy
- `schema_report_b.json` - historical shared-interface conformance report
- `handoff_acknowledgement.md` - acknowledgement given on September 28, 2026; not pilot-exchange approval

Open scientific specifications remain marked as pending rather than being silently fixed.
