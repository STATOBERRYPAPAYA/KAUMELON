# Keep CSS URLs tied to their content so published changes bypass old browser caches.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$hash = (Get-FileHash style.css -Algorithm SHA256).Hash.Substring(0,12).ToLower()
$cssPath = "assets/melon-$hash.css"
Copy-Item style.css $cssPath
$config = Get-Content _quarto.yml -Raw
$config = [regex]::Replace($config, '(?m)^    css: .+$', "    css: $cssPath")
Set-Content _quarto.yml $config
quarto render
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
