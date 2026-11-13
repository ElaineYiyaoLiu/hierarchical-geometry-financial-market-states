# D04 Standalone Resource Probe

This probe uses only predetermined complete graphs and the unchanged public exact-D04 engine. It processes no experimental data and changes no method, tie tolerance, failure mapping or scientific timeout. Actual execution used CPython 3.14.7 on macOS arm64. The exact engine SHA-256 is recorded in `d04-resource-probe.json`.

## Measured cases

| Case | Vertices | Largest equal-edge group | Outcome | Parent wall seconds | Observed peak MiB |
|---|---:|---:|---|---:|---:|
| K4 all equal | 4 | 6 | Completed exactly | 0.059 | 25.20 |
| K5 first seven edges equal, remaining edges strictly ordered | 5 | 7 | Completed exactly | 0.060 | 26.14 |
| K5 all equal | 5 | 10 | Completed exactly | 0.291 | 47.78 |
| K6 all equal | 6 | 15 | Development memory guard | 1.799 | 395.41 |
| K7 all equal | 7 | 21 | Development memory guard | 1.439 | 387.55 |

Parent wall time includes process startup and monitoring. Completed cases also record engine-only time and the worker's own peak-RSS observation. The table takes the maximum of sampled and worker-reported RSS where both are available. Each case in this report was measured once; these are bounded development observations, not representative throughput estimates.

The monitor targeted a sampled 384 MiB guard with a 0.05-second sampling interval; actual peaks can exceed the target between samples. It terminated the two larger cases before their ten-second engine deadline expired. This is neither an observed out-of-memory exception nor a scientific TIMEOUT. The interrupted cases produced no exact answer or final state-count certificate. Completed cases record exact state/hierarchy/ordering counts, nonnegative unit-row-sum checks and exact rational-Jacobian fingerprints.

## Interpretation and next work

Seven equal edges and seven tied vertices describe different workloads: a complete seven-vertex graph has 21 edges. One seven-equal-edge example completed here; the all-equal six/seven-vertex cases did not complete within this probe's memory guard. The earlier expectation of practical large-tie feasibility therefore remains unestablished.

Branch B should review the exact engine's state/memory representation and provide further measurements on the intended processing hardware before using it in the full optimizer. This probe does not authorize a predicted-complexity cutoff, approximate fallback, edge deletion or reclassification of memory limits as TIMEOUT. The actual scientific deadline and failure treatment retain their existing decision gates.

## Reproduction

From the public repository, under Python 3.14 with permission to monitor the child processes:

```text
python branch_b/benchmarks/d04_resource_probe.py --seconds 10 --memory-mib 384 --output d04-resource-probe.json
```

The five cases are declared in the probe source before execution. Each runs in a fresh process; the parent verifies live RSS monitoring before starting, terminates only its own child, and cleans up on monitoring errors. The unchanged engine receives an actual monotonic deadline. Output is write-once and includes source fingerprints and actual outcomes. No scientific bank or source-private path is recorded.

## Monitor verification

The probe now rejects an unavailable preflight measurement before starting workers and stops/reaps a live worker if monitoring is lost. Three operational regressions cover those failures and a normal worker exit during sampling. After that correction, all five cases were rerun under Python 3.14.7; the table and JSON show that execution. The earlier source and measurements remain in commit `b7b1b02f98284f1458bdea946847ff566e0dabce`. The exact engine and completed-case rational Jacobian fingerprints are unchanged.
