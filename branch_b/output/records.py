from __future__ import annotations

from datetime import datetime, timezone


def _base_record(
    *,
    dataset_id: str,
    split: str,
    geometry_id: str,
    common_fitter_id: str,
    schema_version: str,
    parameters: dict,
    diagnostics: dict,
    runtime_seconds: float,
    peak_memory_bytes: int,
    software_environment: dict,
    random_seeds: dict,
    configuration_file: str | None,
) -> dict:
    record = {
        "dataset_id": dataset_id,
        "split": split,
        "geometry_id": geometry_id,
        "common_fitter_id": common_fitter_id,
        "schema_version": schema_version,
        "parameters": parameters,
        "diagnostics": diagnostics,
        "runtime_seconds": runtime_seconds,
        "peak_memory_bytes": peak_memory_bytes,
        "software_environment": software_environment,
        "random_seeds": random_seeds,
        "creation_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if configuration_file is not None:
        record["configuration_file"] = configuration_file
    return record


def build_complete_result(
    *,
    dataset_id: str,
    split: str,
    geometry_id: str,
    common_fitter_id: str,
    schema_version: str,
    sample_order: list[str],
    dissimilarity_matrix: list[list[float]],
    ultrametric_matrix: list[list[float]] | None,
    recovered_tree: dict,
    hierarchy_support: dict,
    bootstrap_stability: float | None,
    parameters: dict,
    diagnostics: dict,
    runtime_seconds: float,
    peak_memory_bytes: int,
    software_environment: dict,
    random_seeds: dict,
    configuration_file: str | None = None,
) -> dict:
    record = _base_record(
        dataset_id=dataset_id,
        split=split,
        geometry_id=geometry_id,
        common_fitter_id=common_fitter_id,
        schema_version=schema_version,
        parameters=parameters,
        diagnostics=diagnostics,
        runtime_seconds=runtime_seconds,
        peak_memory_bytes=peak_memory_bytes,
        software_environment=software_environment,
        random_seeds=random_seeds,
        configuration_file=configuration_file,
    )
    record.update(
        {
            "sample_order": sample_order,
            "dissimilarity_matrix": dissimilarity_matrix,
            "ultrametric_matrix": ultrametric_matrix,
            "recovered_tree": recovered_tree,
            "hierarchy_support": hierarchy_support,
            "bootstrap_stability": bootstrap_stability,
            "status": "complete",
            "failure_code": None,
        }
    )
    return record


def build_failure_result(
    *,
    dataset_id: str,
    split: str,
    geometry_id: str,
    common_fitter_id: str,
    schema_version: str,
    failure_code: str,
    parameters: dict,
    diagnostics: dict,
    runtime_seconds: float,
    peak_memory_bytes: int,
    software_environment: dict,
    random_seeds: dict,
    configuration_file: str | None = None,
) -> dict:
    record = _base_record(
        dataset_id=dataset_id,
        split=split,
        geometry_id=geometry_id,
        common_fitter_id=common_fitter_id,
        schema_version=schema_version,
        parameters=parameters,
        diagnostics=diagnostics,
        runtime_seconds=runtime_seconds,
        peak_memory_bytes=peak_memory_bytes,
        software_environment=software_environment,
        random_seeds=random_seeds,
        configuration_file=configuration_file,
    )
    record.update({"status": "failure", "failure_code": failure_code})
    return record
