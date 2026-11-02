param([string]$PythonExe = '')

$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$venvRoot = Join-Path $repoRoot '.venv'
$venvPython = Join-Path $venvRoot 'Scripts\python.exe'
$backupPath = $null

function Get-PythonInfo {
    param([string]$Executable, [string[]]$Prefix = @())
    try {
        $probe = "import sys,struct; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor)+';'+str(struct.calcsize('P')*8)+';'+sys.executable)"
        $lines = & $Executable @Prefix -c $probe 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $lines) { return $null }
        $parts = ([string]($lines | Select-Object -Last 1)).Split(';', 3)
        if ($parts.Count -ne 3) { return $null }
        return [pscustomobject]@{ Version = $parts[0]; Bits = $parts[1]; Executable = $parts[2] }
    } catch { return $null }
}

function Invoke-PythonStep {
    param([string]$Executable, [string[]]$Arguments)
    # Windows PowerShell 5 can turn ordinary native stderr into an error record.
    # The process exit code, rather than a pip warning, determines success.
    $savedPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $Executable @Arguments
        $stepExitCode = $LASTEXITCODE
    } finally { $ErrorActionPreference = $savedPreference }
    if ($stepExitCode -ne 0) {
        throw ('Python command failed (exit ' + $stepExitCode + '): ' + ($Arguments -join ' '))
    }
}

function Find-Python312 {
    if ($PythonExe) {
        $info = Get-PythonInfo $PythonExe
        if ($info -and $info.Version -eq '3.12' -and $info.Bits -eq '64') { return $info }
        throw '-PythonExe must point to a working Python 3.12 64-bit interpreter.'
    }
    $launcher = Get-Command py -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($launcher) {
        $info = Get-PythonInfo $launcher.Source @('-3.12')
        if ($info -and $info.Version -eq '3.12' -and $info.Bits -eq '64') { return $info }
    }
    $candidates = @(
        (Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Programs\Python\Python312\python.exe'),
        (Join-Path $env:ProgramFiles 'Python312\python.exe')
    )
    $onPath = Get-Command python -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    # Do not launch the Windows Store alias when Python has not been installed.
    if ($onPath -and $onPath.Source -notlike '*\Microsoft\WindowsApps\python.exe') {
        $candidates += $onPath.Source
    }
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $info = Get-PythonInfo $candidate
            if ($info -and $info.Version -eq '3.12' -and $info.Bits -eq '64') { return $info }
        }
    }
    throw ('Python 3.12 64-bit was not found. Install it with pip, venv and Tcl/Tk, then run CAI_DAT.bat again. ' +
        'Download: https://www.python.org/downloads/release/python-31210/ . See README.md. ' +
        'For a custom location, run this script with -PythonExe followed by the full python.exe path.')
}

Push-Location -LiteralPath $repoRoot
try {
    # Locate and validate the base interpreter before touching an existing venv.
    $base = Find-Python312
    Write-Host ('Python selected: ' + $base.Executable + ' (3.12, 64-bit)')
    Invoke-PythonStep $base.Executable @('-c', "import tkinter,venv,ensurepip; print('Base Python components: OK')")

    $item = $null
    if (Test-Path -LiteralPath $venvRoot) {
        $item = Get-Item -LiteralPath $venvRoot -Force
        if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw '.venv must be a regular directory; move a linked/custom environment manually before installing.'
        }
    }
    $existing = $null
    if (Test-Path -LiteralPath $venvPython -PathType Leaf) { $existing = Get-PythonInfo $venvPython }
    if (Test-Path -LiteralPath $venvRoot) {
        if (-not $existing -or $existing.Version -ne '3.12' -or $existing.Bits -ne '64') {
            $suffix = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
            $backupPath = [IO.Path]::GetFullPath((Join-Path $repoRoot ('.venv.backup-' + $suffix)))
            # Both absolute directory paths must be direct children of this repo.
            foreach ($target in @($item.FullName, $backupPath)) {
                if (-not [string]::Equals([IO.Path]::GetDirectoryName($target), $repoRoot, [StringComparison]::OrdinalIgnoreCase)) {
                    throw 'Environment backup path is outside the project directory.'
                }
            }
            if (Test-Path -LiteralPath $backupPath) { throw 'Environment backup path already exists.' }
            Write-Host ('Backing up the old/broken environment to ' + $backupPath)
            Move-Item -LiteralPath $item.FullName -Destination $backupPath
        }
    }
    if (-not (Test-Path -LiteralPath $venvRoot)) {
        Invoke-PythonStep $base.Executable @('-m', 'venv', $venvRoot)
    }
    $installed = Get-PythonInfo $venvPython
    if (-not $installed -or $installed.Version -ne '3.12' -or $installed.Bits -ne '64') {
        throw 'The project environment is not Python 3.12 64-bit.'
    }
    Invoke-PythonStep $venvPython @('-m', 'pip', 'install', '--upgrade', 'pip')
    Invoke-PythonStep $venvPython @('-m', 'pip', 'install', '--only-binary=:all:', '-r', (Join-Path $repoRoot 'requirements.txt'))
    Invoke-PythonStep $venvPython @('-m', 'pip', 'check')
    Invoke-PythonStep $venvPython @('-m', 'compileall', '-q', 'pps', 'main.py', 'exam_cli.py')
    Invoke-PythonStep $venvPython @('-c', "import sys,numpy,scipy,sympy,matplotlib,openpyxl,PIL,tkinter; import pps.gui,pps.inverse_presentation; print('Environment ready:',sys.version.split()[0]); print('Interpreter:',sys.executable)")
    Write-Host 'Setup complete. Open CHAY_PPS.bat to start the application.'
    if ($backupPath) { Write-Host ('Old environment preserved at: ' + $backupPath) }
} catch {
    Write-Host ('SETUP FAILED: ' + $_.Exception.Message) -ForegroundColor Red
    if ($backupPath) { Write-Host ('Old environment backup retained: ' + $backupPath) }
    exit 1
} finally { Pop-Location }
exit 0
