$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..")
Push-Location $repoRoot
try {
python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --console `
  --name eastmoney_buyback_01810 `
  --paths scripts\data_analysis `
  scripts\data_analysis\eastmoney_buyback_01810.py
} finally {
  Pop-Location
}
