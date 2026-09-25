# File contract audit

The shared contract defines observable-dataset, manifest, and Branch B-output schemas. Observable dataset IDs and sample IDs are opaque; manifests carry checksums; matrices use canonical sample order; path traversal is rejected; observable CSV payloads are opened and checksum/header/row/order/numeric values are validated.

Branch A's development handoff rehearsal validates generated observable metadata and manifests against a pinned shared-contract snapshot. Restricted truth is written separately and is not included in the observable manifest.

Pilot exchange remains blocked on the Branch B pre-pilot method gates and Faculty Advisor approval.
