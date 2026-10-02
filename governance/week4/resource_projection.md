# Resource projection framework

Status: UNMEASURED. No synthetic benchmark values are inserted.

Collect permitted aggregate wall seconds, allocated core-hours, peak memory, bytes per dataset, queue seconds, bootstrap counts, failed fits and effective throughput. Record stage, measured hardware, configuration/version, intended dataset count, repetition/bootstrap counts, concurrency and available budget. Include failed scheduled attempts and all registered geometry/candidate-fitter combinations. Model preprocessing, selection, fitting, bootstrap, independent banks, sensitivity work, reconciliation and retries explicitly to avoid omission or double counting.

For each stage: projected core-hours = measured core-hours per attempt × planned attempts; storage GiB = bytes per attempt × planned attempts / 2^30; serial elapsed hours = measured wall seconds per attempt × planned attempts / 3600. A concurrency-adjusted elapsed projection is valid only with measured effective throughput and measured queue overhead. Peak memory is a concurrency constraint, not an average. Sum stage costs; separately record retention copies and capacity headroom. PL must approve feasibility against actual capacity.

These are accounting formulas. No repetitions, headroom multiplier, statistical criterion or trigger is fixed here. Truth-keyed per-condition resource information requires an authorized conservative aggregate release. Keep projected values blank until benchmark evidence exists.
