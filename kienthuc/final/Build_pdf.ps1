param([string]$Compiler = 'xelatex')
$ErrorActionPreference = 'Stop'
$manualRoot = $PSScriptRoot
$buildRoot = Join-Path $manualRoot 'build'
New-Item -ItemType Directory -Path $buildRoot -Force | Out-Null
$compilerCommand = Get-Command $Compiler -ErrorAction Stop
Push-Location -LiteralPath $manualRoot
try {
  foreach ($document in @('So_tay_PPS', 'Tien_xu_ly_Excel')) {
    # Three passes resolve page references, TOC widths and PDF bookmarks.
    for ($pass = 1; $pass -le 3; $pass++) {
        $passLog = Join-Path $buildRoot ($document + '_compile_' + $pass + '.txt')
        & $compilerCommand.Source --disable-installer -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build ($document + '.tex') *> $passLog
        if ($LASTEXITCODE -ne 0) {
            Get-Content -LiteralPath $passLog -Tail 35
            throw "XeLaTeX failed (pass $pass). See $passLog"
        }
    }
    $texLog = Get-Content -LiteralPath (Join-Path $buildRoot ($document + '.log')) -Raw
    if ($texLog -match 'undefined references|Missing character|Overfull \\[hv]box') {
        throw ('Review PDF layout/reference warnings in build/' + $document + '.log before publishing.')
    }
    Copy-Item -LiteralPath (Join-Path $buildRoot ($document + '.pdf')) -Destination (Join-Path $manualRoot ($document + '.pdf')) -Force
    Write-Output ('PDF ready: kienthuc/final/' + $document + '.pdf')
  }
} finally {
    Pop-Location
}
