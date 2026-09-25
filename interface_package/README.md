# Interface package

This directory contains the versioned machine-readable contracts used for shared project handoffs.

The shared pilot interface covers three artifacts:

- `observable_dataset.schema.json`
- `branch_b_output.schema.json`
- `manifest.schema.json`

Sealed ground truth and its internal serialization belong to the restricted Branch A side and are not part of the Branch B-facing interface.

Shared schema changes are versioned and recorded through project governance. The recovered-tree representation used by the Branch B output interface is a JSON edge list with the root, internal nodes, leaves, directed parent-child edges, branch lengths, unresolved relations, and zero-length branches.
