<#
.SYNOPSIS
  Runs Atomic Red Team tests and exports the resulting events as a Mordor-style
  dataset with known ATT&CK ground truth.

.DESCRIPTION
  For each technique: prerequisites, the test, then cleanup. Afterwards every
  Sysmon, Security, PowerShell and System event written since the start is
  exported as JSON lines (one event per line, OTRF field style) and zipped to

    <OutputRoot>\<Name>\acquisitions\<Name>.zip
    <OutputRoot>\<Name>\expected.json   (techniques run, test numbers, start/end)

  OutputRoot is shared with the Mac (Vagrant/UTM shared folder), so the dataset appears
  under $TEST_IMAGES_PATH/mordor/lab/<Name>.

.EXAMPLE
  .\Invoke-MordorCapture.ps1 -Name lab_persistence -Techniques T1547.001,T1053.005
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string[]]$Techniques,
    [string]$OutputRoot = "C:\lab\mordor\lab",
    [int[]]$TestNumbers = @(1),
    [int]$SettleSeconds = 15
)
$ErrorActionPreference = "Stop"
Import-Module "C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1" -Force
$PSDefaultParameterValues = @{ "Invoke-AtomicTest:PathToAtomicsFolder" = "C:\AtomicRedTeam\atomics" }

$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
$dir = Join-Path $OutputRoot $Name
$acq = Join-Path $dir "acquisitions"
New-Item -ItemType Directory -Force -Path $acq | Out-Null

$start = Get-Date
$ran = @()
foreach ($t in $Techniques) {
    foreach ($n in $TestNumbers) {
        Write-Host "`n== $t test $n ==" -ForegroundColor Cyan
        try {
            Invoke-AtomicTest $t -TestNumbers $n -GetPrereqs | Out-Null
            Invoke-AtomicTest $t -TestNumbers $n
            $ran += [pscustomobject]@{ technique = $t; test = $n; result = "ran" }
        } catch {
            Write-Host "  $t #$n failed: $_" -ForegroundColor Yellow
            $ran += [pscustomobject]@{ technique = $t; test = $n; result = "error: $_" }
        } finally {
            Invoke-AtomicTest $t -TestNumbers $n -Cleanup -ErrorAction SilentlyContinue | Out-Null
        }
    }
}
Start-Sleep -Seconds $SettleSeconds
$end = Get-Date

$channels = @(
    "Microsoft-Windows-Sysmon/Operational",
    "Security",
    "Microsoft-Windows-PowerShell/Operational",
    "Windows PowerShell",
    "System"
)
$jsonPath = Join-Path $env:TEMP "$Name.json"
$count = 0
$writer = [IO.StreamWriter]::new($jsonPath, $false, [Text.UTF8Encoding]::new($false))
try {
    foreach ($ch in $channels) {
        $events = Get-WinEvent -FilterHashtable @{ LogName = $ch; StartTime = $start; EndTime = $end } -ErrorAction SilentlyContinue
        foreach ($e in $events) {
            $x = [xml]$e.ToXml()
            $rec = [ordered]@{
                "@timestamp"  = $e.TimeCreated.ToUniversalTime().ToString("o")
                Hostname      = $e.MachineName
                Channel       = $e.LogName
                EventID       = $e.Id
                ProviderName  = $e.ProviderName
                RecordNumber  = $e.RecordId
                ProcessID     = $e.ProcessId
                Level         = $e.LevelDisplayName
                Message       = $e.Message
            }
            foreach ($d in $x.Event.EventData.Data) { if ($d.Name) { $rec[$d.Name] = $d.'#text' } }
            $writer.WriteLine(($rec | ConvertTo-Json -Compress -Depth 4))
            $count++
        }
    }
} finally {
    $writer.Dispose()
}

$zip = Join-Path $acq "$Name.zip"
Compress-Archive -Path $jsonPath -DestinationPath $zip -Force
[ordered]@{
    name       = $Name
    host       = $env:COMPUTERNAME
    start      = $start.ToUniversalTime().ToString("o")
    end        = $end.ToUniversalTime().ToString("o")
    events     = $count
    techniques = $ran
} | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $dir "expected.json") -Encoding UTF8
Remove-Item $jsonPath

Write-Host "`n[+] $count events -> $zip" -ForegroundColor Green
