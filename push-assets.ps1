<#
.SYNOPSIS
    Install the client dependencies locally and upload the vendored assets
    to the server via SCP.

.DESCRIPTION
    Runs npm install and grunt copy in the project root to (re)generate
    lnto/static/vendor/ from node_modules, then uploads that directory to
    the remote server.

    Connection settings are read from .env in the project root.
    Copy .env.example to .env and fill in your values.

.EXAMPLE
    .\push-assets.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Load connection settings from .env ──────────────────

$Root = $PSScriptRoot
$EnvFile = Join-Path $Root ".env"

if (-not (Test-Path $EnvFile)) {
    Write-Error ".env not found. Copy .env.example to .env and fill in your connection details."
    exit 1
}

$EnvVars = @{}
foreach ($Line in Get-Content $EnvFile) {
    $Line = $Line.Trim()
    if ($Line -eq '' -or $Line.StartsWith('#')) { continue }
    $EqIndex = $Line.IndexOf('=')
    if ($EqIndex -lt 1) { continue }
    $Key = $Line.Substring(0, $EqIndex).Trim()
    $Value = $Line.Substring($EqIndex + 1).Trim().Trim('"').Trim("'")
    $EnvVars[$Key] = $Value
}

$RemoteUser = $EnvVars['REMOTE_USER']
$RemoteHost = $EnvVars['REMOTE_HOST']
$RemotePath = $EnvVars['REMOTE_PATH']
$RemotePort = if ($EnvVars['REMOTE_PORT']) { $EnvVars['REMOTE_PORT'] } else { "22" }

# ── Script ──────────────────────────────────────────────────────────

$VendorDir = Join-Path $Root "lnto" | Join-Path -ChildPath "static" | Join-Path -ChildPath "vendor"
# Remote destination: <REMOTE_PATH>/lnto/static/  (scp -r appends "vendor")
$RemoteDest = "${RemoteUser}@${RemoteHost}:${RemotePath}/lnto/static/"

function Ok   { param([string]$Msg) Write-Host "  $Msg" -ForegroundColor Green }
function Fail { param([string]$Msg) Write-Error $Msg; exit 1 }

if (-not $RemoteUser -or -not $RemoteHost -or -not $RemotePath) {
    Fail "REMOTE_USER, REMOTE_HOST, and REMOTE_PATH must be set in .env."
}

# 1. Install client dependencies

Write-Host "Installing npm dependencies..."
npm install --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { Fail "npm install failed." }
Ok "npm dependencies installed."

# 2. Vendor the assets (copies built files from node_modules into lnto/static/vendor)

Write-Host "Running grunt copy..."
npx grunt copy
if ($LASTEXITCODE -ne 0) { Fail "grunt copy failed." }

$VendorFiles = Get-ChildItem $VendorDir -Recurse -File
if (-not $VendorFiles -or $VendorFiles.Count -eq 0) {
    Fail "No vendored files found in $VendorDir."
}
Ok "Vendored $($VendorFiles.Count) files into lnto/static/vendor/."

# 3. Upload via SCP

Write-Host "Uploading $VendorDir -> $RemoteDest ..."
scp.exe -P $RemotePort -r $VendorDir $RemoteDest
if ($LASTEXITCODE -ne 0) { Fail "SCP upload failed." }
Ok "Assets uploaded."

# 4. Fix file permissions (scp can strip read bits)

Write-Host "Fixing permissions on server..."
ssh.exe -p $RemotePort "${RemoteUser}@${RemoteHost}" "chmod -R u+rwX,go+rX '${RemotePath}/lnto/static/vendor'"
if ($LASTEXITCODE -ne 0) { Fail "chmod failed." }
Ok "Permissions fixed."

Write-Host ""
Ok "Done. Client assets are current on the server."
