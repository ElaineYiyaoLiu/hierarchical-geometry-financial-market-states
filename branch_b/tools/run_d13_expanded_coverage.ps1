# Branch B D13 expanded synthetic coverage, Python 3.14 ONLY.
# Run from repository root. This study is NOT scientific certification.
# Repeat the command to resume. No calibration/hidden data is read.
param(
    [int]$MaxNewTrials = 100,
    [string]$EvidenceDir = ""
)
$ErrorActionPreference = "Stop"
$version = & python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"
if ($LASTEXITCODE -ne 0 -or -not $version.StartsWith("3.14.")) {
    throw "Actual Python 3.14 required; found: $version"
}
$root = & git rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) { throw "Repository root unavailable" }
Set-Location $root
if ([string]::IsNullOrWhiteSpace($EvidenceDir)) {
    $EvidenceDir = Join-Path (Split-Path -Parent $root) "local-d13-expanded-coverage"
}
$EvidenceDir = [System.IO.Path]::GetFullPath($EvidenceDir)
$repoPrefix = [System.IO.Path]::GetFullPath($root).TrimEnd([char]92, [char]47) + [System.IO.Path]::DirectorySeparatorChar
if ($EvidenceDir.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "EvidenceDir must be outside the public shared repository."
}
New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null
$runLog = Join-Path $EvidenceDir "runs.log"
$manifest = Join-Path $EvidenceDir "local-machine-provenance.txt"
if (Test-Path $manifest) {
    $savedVersion = Select-String -Path $manifest -Pattern '^python_version=' | Select-Object -First 1
    if ($null -eq $savedVersion -or $savedVersion.Line -ne "python_version=$version") {
        throw "Python version differs from the original study run."
    }
    $savedChecksums = Join-Path $EvidenceDir "source-sha256.txt"
    if (-not (Test-Path $savedChecksums)) { throw "Original source checksums missing." }
    foreach ($line in Get-Content $savedChecksums) {
        $parts = $line -split '\\s+', 2
        if ($parts.Count -ne 2 -or (Get-FileHash -Algorithm SHA256 -Path $parts[1].Trim()).Hash -ne $parts[0]) {
            throw "Source changed during resumed study; preserve results for review."
        }
    }
}
if (-not (Test-Path $manifest)) {
    "python_version=$version" | Set-Content $manifest
    "git_head=$(& git rev-parse HEAD)" | Add-Content $manifest
    "git_branch=$(& git branch --show-current)" | Add-Content $manifest
    & python -m pip freeze | Set-Content (Join-Path $EvidenceDir "python314-freeze.txt")
    if ($LASTEXITCODE -ne 0) { throw "Dependency capture failed" }
    $paths = @(
        "branch_b/tools/d13_expanded_synthetic_coverage.py",
        "branch_b/bootstrap/development_d13_interval.py",
        "branch_b/tools/d13_synthetic_coverage.py"
    )
    foreach ($path in $paths) {
        "$((Get-FileHash -Algorithm SHA256 -Path $path).Hash)  $path" |
            Add-Content (Join-Path $EvidenceDir "source-sha256.txt")
    }
}
# The python study checks its original design manifest, preserving all earlier
# trial records. Do not erase or reset this folder after inspecting results.
"run_started_utc=$((Get-Date).ToUniversalTime().ToString('o'))" | Add-Content $runLog
& python -m branch_b.tools.d13_expanded_synthetic_coverage --output-dir $EvidenceDir --max-new-trials $MaxNewTrials 2>&1 |
    Tee-Object -FilePath (Join-Path $EvidenceDir "latest-output.txt")
if ($LASTEXITCODE -ne 0) { throw "Expanded D13 diagnostics failed; journal preserved." }
Get-Content (Join-Path $EvidenceDir "latest-output.txt") | Add-Content $runLog
"run_finished_utc=$((Get-Date).ToUniversalTime().ToString('o'))" | Add-Content $runLog
Write-Host "Evidence folder: $EvidenceDir"
Write-Host "Review summary.json. Repeat this command to resume until all_cells_complete=true."
Write-Host "Do not publish local evidence without Branch B and public-disclosure checks."
