# Branch B synthetic-only D13 / full regression evidence capture.
# Invoke from repository root with Python 3.14 activated.
# Evidence stays LOCAL. Review contents before sharing.
$ErrorActionPreference = "Stop"
$version = & python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"
if ($LASTEXITCODE -ne 0 -or -not $version.StartsWith("3.14.")) {
    throw "Required actual Python 3.14 interpreter unavailable: $version"
}
$root = & git rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) { throw "Not in a Git working tree." }
Set-Location $root
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$evidenceDir = Join-Path $root ("local-d13-evidence-" + $stamp)
New-Item -ItemType Directory -Path $evidenceDir | Out-Null
$metadata = Join-Path $evidenceDir "environment.txt"
"python_version=$version" | Set-Content -Path $metadata
"git_head=$(& git rev-parse HEAD)" | Add-Content $metadata
"git_branch=$(& git branch --show-current)" | Add-Content $metadata
"git_status_begin" | Add-Content $metadata
& git status --short | Add-Content $metadata
"git_status_end" | Add-Content $metadata
& python -m pip freeze | Set-Content (Join-Path $evidenceDir "python314-freeze.txt")
if ($LASTEXITCODE -ne 0) { throw "pip freeze failed" }
& python -m pip check 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDir "pip-check.txt")
if ($LASTEXITCODE -ne 0) { throw "pip check failed" }
$checks = @(
  "branch_b/bootstrap/development_d13_interval.py",
  "branch_b/tools/d13_synthetic_coverage.py",
  "branch_b/recovery_tests/test_development_d13_interval.py",
  "branch_b/recovery_tests/test_development_d13_statistical_diagnostics.py",
  "branch_b/recovery_tests/test_d13_synthetic_coverage_runner.py"
)
foreach ($p in $checks) {
    if (-not (Test-Path $p)) { throw "Required file not found: $p" }
    $hash = (Get-FileHash -Algorithm SHA256 -Path $p).Hash
    "$hash  $p" | Add-Content (Join-Path $evidenceDir "source-sha256.txt")
}
& python -m pytest -q branch_b/recovery_tests/test_development_d13_interval.py branch_b/recovery_tests/test_development_d13_statistical_diagnostics.py branch_b/recovery_tests/test_d13_synthetic_coverage_runner.py --basetemp=".pytest_tmp_d13" "--junitxml=$evidenceDir/d13-focused.xml" 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDir "d13-focused.txt")
if ($LASTEXITCODE -ne 0) { throw "Focused D13 tests failed; see local evidence" }
& python -m branch_b.tools.d13_synthetic_coverage --trials 48 --sample-size 24 --seed 314159 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDir "synthetic-coverage.json")
if ($LASTEXITCODE -ne 0) { throw "Synthetic coverage run failed" }
& python -m pytest -q --basetemp=".pytest_tmp_314" "--junitxml=$evidenceDir/full-regression.xml" 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDir "full-regression.txt")
if ($LASTEXITCODE -ne 0) { throw "Full regression failed; see local evidence" }
Get-ChildItem -Path $evidenceDir -File | ForEach-Object {
    "$((Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash)  $($_.Name)"
} | Set-Content (Join-Path $evidenceDir "artifact-sha256.txt")
Write-Host "D13 development validation finished. Local evidence: $evidenceDir"
Write-Host "This is NOT a scientific freeze or statistical coverage certification."
