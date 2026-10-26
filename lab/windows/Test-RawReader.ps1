<#
.SYNOPSIS
  Compares Gandalf's raw NTFS reader (GandalfNtfs, in Set-ArtefactCollection) with
  RawCopy on locked files and NTFS metafiles: size, SHA256 and time for each.

.DESCRIPTION
  Loads the reader from the Gandalf copy in the VM, so it tests what Invoke-Gandalf
  runs. RawCopy comes from tools\disk_tools.zip; without it only the reader runs.
  Prints one CSV line per file: File,ReaderBytes,RawCopyBytes,Match,ReaderSeconds,RawCopySeconds
#>
[CmdletBinding()]
param(
    [string]$GandalfSource = "C:\lab\gandalf-src",
    [string]$Work = "C:\lab\rawcheck"
)
$ErrorActionPreference = "Stop"

$Collection = Get-Content -Raw -LiteralPath (Join-Path $GandalfSource "windows\Set-ArtefactCollection")
$Source = [regex]::Match($Collection, "(?s)Add-Type -TypeDefinition @'\r?\n(.*?)\r?\n'@")
if (-not $Source.Success) { throw "GandalfNtfs source not found in Set-ArtefactCollection" }
Add-Type -TypeDefinition $Source.Groups[1].Value

$Tools = Join-Path $GandalfSource "tools"
if (Test-Path -LiteralPath "$Tools\disk_tools.zip") { Expand-Archive -LiteralPath "$Tools\disk_tools.zip" -DestinationPath $Tools -Force }
$RawCopy = Join-Path $Tools "RawCopy64.exe"
$HaveRawCopy = Test-Path -LiteralPath $RawCopy

Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "$Work\reader", "$Work\rawcopy" | Out-Null

$Started = Get-Date
$Ntfs = New-Object GandalfNtfs("C:")
Write-Output ("# reader opened C: in {0:N1}s (cluster {1}, record {2})" -f ((Get-Date) - $Started).TotalSeconds, $Ntfs.ClusterSize, $Ntfs.RecordSize)

# Path for the reader, and the name RawCopy gives it (RawCopy takes C:0 for record 0)
$Checks = @(
    @{ Path = 'C:\$MFT'; Record = 0; RawCopyPath = "C:0"; Name = '$MFT' },
    @{ Path = 'C:\$LogFile'; Record = 2; RawCopyPath = "C:2"; Name = '$LogFile' },
    @{ Path = 'C:\$Extend\$UsnJrnl:$J'; Name = '$J' },
    @{ Path = "C:\Windows\System32\config\SYSTEM" },
    @{ Path = "C:\Windows\System32\config\SOFTWARE" },
    @{ Path = "C:\Windows\System32\config\SAM" },
    @{ Path = "C:\Windows\System32\config\SYSTEM.LOG1" },
    @{ Path = "C:\Windows\AppCompat\Programs\Amcache.hve" },
    @{ Path = "C:\Windows\System32\sru\SRUDB.dat" },
    @{ Path = "C:\Windows\INF\setupapi.dev.log" },
    @{ Path = "C:\swapfile.sys" },
    @{ Path = "$env:USERPROFILE\NTUSER.DAT" },
    @{ Path = "C:\ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb" },
    @{ Path = "C:\ProgramData\Microsoft\Network\Downloader\qmgr.db" }
)

Write-Output "File,ReaderBytes,RawCopyBytes,Match,ReaderSeconds,RawCopySeconds"
foreach ($Check in $Checks) {
    $Name = if ($Check.Name) { $Check.Name } else { Split-Path -Leaf $Check.Path }
    $ReaderOut = Join-Path "$Work\reader" $Name
    $ReaderBytes = ""; $ReaderSeconds = ""; $RawCopyBytes = ""; $RawCopySeconds = ""; $Match = ""
    try {
        $t = Get-Date
        if ($Check.ContainsKey("Record")) { [void]$Ntfs.CopyRecord($Check.Record, "", $ReaderOut, $false) }
        else { [void]$Ntfs.CopyFile($Check.Path, $ReaderOut) }
        $ReaderSeconds = "{0:N1}" -f ((Get-Date) - $t).TotalSeconds
        $ReaderBytes = (Get-Item -LiteralPath $ReaderOut).Length
    }
    catch { $ReaderBytes = "error: $($_.Exception.Message -replace ',', ';')" }
    if ($HaveRawCopy -and $Name -ne '$J') {
        $Target = if ($Check.RawCopyPath) { $Check.RawCopyPath } else { $Check.Path }
        $t = Get-Date
        & $RawCopy "/FileNamePath:$Target" "/OutputPath:$Work\rawcopy" | Out-Null
        $RawCopySeconds = "{0:N1}" -f ((Get-Date) - $t).TotalSeconds
        $RawCopyOut = Join-Path "$Work\rawcopy" $Name
        if (Test-Path -LiteralPath $RawCopyOut) {
            $RawCopyBytes = (Get-Item -LiteralPath $RawCopyOut).Length
            if (Test-Path -LiteralPath $ReaderOut) {
                $Match = ((Get-FileHash -LiteralPath $ReaderOut).Hash -eq (Get-FileHash -LiteralPath $RawCopyOut).Hash)
            }
        }
        else { $RawCopyBytes = "no output" }
    }
    Write-Output "$Name,$ReaderBytes,$RawCopyBytes,$Match,$ReaderSeconds,$RawCopySeconds"
}
$Ntfs.Dispose()
Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue
