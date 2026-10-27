<#
.SYNOPSIS
  Compares Gandalf's raw NTFS reader (GandalfNtfs, in Set-ArtefactCollection) with
  RawCopy on locked files and NTFS metafiles, and records why any copies differ.

.DESCRIPTION
  Two passes over the same files:

  Live      the reader, RawCopy, the reader again, then RawCopy again, all off the
            running C:. Windows keeps writing to these files, so copies taken minutes
            apart can differ. Every block where the reader and RawCopy disagree is classed:
              changed         either tool's two passes differ there too, so the file was
                              written during the run
              tools disagree  each tool is consistent with itself but they differ: one
                              of them reads that block wrongly (the snapshot pass says which)
  Snapshot  the reader and an independent copy (RawCopy by record number for
            metafiles, Windows' own file copy for the rest) off one VSS snapshot.
            Nothing moves, so any difference is a reader bug ("mismatch").

  For $MFT records the detail names the file, the attribute that differs, and the
  LSN, sequence number and in-use flag from each copy; for $LogFile pages the last LSN; for hives the base
  block's sequence numbers.

  Writes to $Report: summary.csv (a row per file and pass, with the cause),
  blocks.csv (a row per differing block) and run.json, and prints the summary.
  RawCopy comes from tools\disk_tools.zip; without it only the reader runs.
#>
[CmdletBinding()]
param(
    [string]$GandalfSource = "C:\lab\gandalf-src",
    [string]$Work = "C:\lab\rawcheck",
    [string]$Report = "C:\lab\rawcheck-report",
    # blocks.csv rows per file and pass; the summary counts all of them regardless
    [int]$MaxBlockRows = 20000
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

Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;

public class RawCheckBlock { public long Block; public long Offset; public string Class; public string Detail; }

public static class RawCheckDiff {
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    static extern SafeFileHandle CreateFile(string name, uint access, uint share, IntPtr security, uint disposition, uint flags, IntPtr template);

    // A VSS snapshot's device (\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopyN), for GandalfNtfs(Stream, 0)
    public static FileStream OpenDevice(string device) {
        SafeFileHandle h = CreateFile(device, 0x80000000, 3, IntPtr.Zero, 3, 0, IntPtr.Zero);
        if (h.IsInvalid) throw new IOException("cannot open " + device + " (error " + Marshal.GetLastWin32Error() + ")");
        return new FileStream(h, FileAccess.Read, 1);
    }

    static int Fill(Stream s, byte[] b) {
        int got = 0;
        while (got < b.Length) { int n = s.Read(b, got, b.Length - got); if (n <= 0) break; got += n; }
        for (int i = got; i < b.Length; i++) b[i] = 0;
        return got;
    }

    static bool Zero(byte[] a) { for (int i = 0; i < a.Length; i++) if (a[i] != 0) return false; return true; }

    static bool Same(byte[] a, byte[] b) { for (int i = 0; i < a.Length; i++) if (a[i] != b[i]) return false; return true; }

    // Blocks where a (reader) and b (reference) differ. c and d are each tool's second
    // pass (live only, else null): where either differs from its first pass the file was
    // written during the run. Counts every differing block; details for the first maxRows.
    public static List<RawCheckBlock> Compare(string a, string b, string c, string d, int size, string kind, int maxRows, out long total, out long changed) {
        List<RawCheckBlock> rows = new List<RawCheckBlock>();
        total = 0; changed = 0;
        using (FileStream fa = File.OpenRead(a)) using (FileStream fb = File.OpenRead(b)) {
            // PowerShell passes $null to a string parameter as ""
            FileStream fc = string.IsNullOrEmpty(c) ? null : File.OpenRead(c);
            FileStream fd = string.IsNullOrEmpty(d) ? null : File.OpenRead(d);
            try {
                byte[] ba = new byte[size], bb = new byte[size], bc = new byte[size], bd = new byte[size];
                for (long block = 0; ; block++) {
                    int na = Fill(fa, ba), nb = Fill(fb, bb);
                    if (fc != null) Fill(fc, bc);
                    if (fd != null) Fill(fd, bd);
                    if (na == 0 && nb == 0) break;
                    if (na == nb && Same(ba, bb)) continue;
                    total++;
                    string cls;
                    if (fc == null) cls = "mismatch";
                    else if (!Same(ba, bc) || (fd != null && !Same(bb, bd))) cls = "changed";
                    else cls = fd == null ? "unexplained" : "tools disagree";
                    if (cls == "changed") changed++;
                    if (rows.Count < maxRows) {
                        RawCheckBlock row = new RawCheckBlock();
                        row.Block = block; row.Offset = block * size; row.Class = cls;
                        row.Detail = Describe(kind, ba, bb, fc == null ? null : bc);
                        // Past a file's valid data length NTFS reads zeros, whatever the clusters hold
                        if (cls != "changed" && Zero(ba) && !Zero(bb))
                            row.Detail = "past the valid data length: reader zeros, reference stale clusters" + (row.Detail == "" ? "" : "; " + row.Detail);
                        rows.Add(row);
                    }
                }
            }
            finally { if (fc != null) fc.Dispose(); if (fd != null) fd.Dispose(); }
        }
        return rows;
    }

    static string Magic(byte[] r) { return Encoding.ASCII.GetString(r, 0, 4); }

    static string Trio(object a, object b, object c, bool hex) {
        string f = hex ? "0x{0:X}" : "{0}";
        string s = string.Format(f, a) + " -> " + string.Format(f, b);
        return c == null ? s : s + " -> " + string.Format(f, c);
    }

    static string Describe(string kind, byte[] a, byte[] b, byte[] c) {
        try {
            if (kind == "mft") return Mft(a, b, c);
            if (kind == "logfile") {
                if (Magic(b) == "RSTR") return "restart area rewritten";
                if (Magic(b) == "RCRD")
                    return "log page rewritten; last LSN " + Trio(BitConverter.ToUInt64(a, 8), BitConverter.ToUInt64(b, 8), c == null ? null : (object)BitConverter.ToUInt64(c, 8), true);
                return "log page";
            }
            if (kind == "hive") {
                if (Magic(b) == "regf")
                    return "base block rewritten (hive flushed); sequence " + Trio(BitConverter.ToUInt32(a, 4), BitConverter.ToUInt32(b, 4), c == null ? null : (object)BitConverter.ToUInt32(c, 4), false);
                if (Magic(b) == "hbin") return "hive bin rewritten";
                return "hive data";
            }
        }
        catch (Exception e) { return "undecoded: " + e.Message; }
        return "";
    }

    // A copy of an MFT record with the update sequence array put back
    static byte[] Fixup(byte[] r) {
        byte[] c = (byte[])r.Clone();
        if (c.Length < 48 || Magic(c) != "FILE") return c;
        int usa = BitConverter.ToUInt16(c, 4), n = BitConverter.ToUInt16(c, 6);
        for (int i = 1; i < n; i++) {
            int end = i * 512 - 2;
            if (end + 1 >= c.Length || usa + 2 * i + 1 >= c.Length) break;
            c[end] = c[usa + 2 * i]; c[end + 1] = c[usa + 2 * i + 1];
        }
        return c;
    }

    // The record's $FILE_NAME, the Win32 one over the 8.3 one
    static string MftName(byte[] r) {
        if (Magic(r) != "FILE") return "";
        string best = "";
        int at = BitConverter.ToUInt16(r, 0x14);
        while (at + 8 <= r.Length) {
            uint type = BitConverter.ToUInt32(r, at);
            if (type == 0xFFFFFFFF) break;
            int len = (int)BitConverter.ToUInt32(r, at + 4);
            if (len <= 0 || at + len > r.Length) break;
            if (type == 0x30 && r[at + 8] == 0) {
                int co = at + BitConverter.ToUInt16(r, at + 0x14);
                if (co + 0x42 <= r.Length) {
                    int nl = r[co + 0x40], ns = r[co + 0x41];
                    if (co + 0x42 + nl * 2 <= r.Length && (best == "" || ns != 2)) best = Encoding.Unicode.GetString(r, co + 0x42, nl * 2);
                }
            }
            at += len;
        }
        return best;
    }

    static string AttributeName(uint type) {
        switch (type) {
            case 0x10: return "$STANDARD_INFORMATION"; case 0x20: return "$ATTRIBUTE_LIST"; case 0x30: return "$FILE_NAME";
            case 0x40: return "$OBJECT_ID"; case 0x50: return "$SECURITY_DESCRIPTOR"; case 0x60: return "$VOLUME_NAME";
            case 0x70: return "$VOLUME_INFORMATION"; case 0x80: return "$DATA"; case 0x90: return "$INDEX_ROOT";
            case 0xA0: return "$INDEX_ALLOCATION"; case 0xB0: return "$BITMAP"; case 0xC0: return "$REPARSE_POINT";
            case 0x100: return "$LOGGED_UTILITY_STREAM"; default: return string.Format("attribute 0x{0:X}", type);
        }
    }

    // Where two fixed-up records first differ: the header, an attribute, or the slack after them
    static string DiffersIn(byte[] a, byte[] b) {
        int first = -1;
        for (int i = 0; i < a.Length; i++) if (a[i] != b[i]) { first = i; break; }
        if (first < 0) return "";
        if (Magic(b) != "FILE") return "offset " + first;
        int at = BitConverter.ToUInt16(b, 0x14);
        if (first < at) return "record header";
        while (at + 8 <= b.Length) {
            uint type = BitConverter.ToUInt32(b, at);
            if (type == 0xFFFFFFFF) break;
            int len = (int)BitConverter.ToUInt32(b, at + 4);
            if (len <= 0 || at + len > b.Length) break;
            if (first < at + len) return AttributeName(type);
            at += len;
        }
        return "slack after the attributes";
    }

    static string Mft(byte[] a, byte[] b, byte[] c) {
        byte[] fa = Fixup(a), fb = Fixup(b), fc = c == null ? null : Fixup(c);
        if (Magic(fa) != "FILE" && Magic(fb) != "FILE") return "not a FILE record in either copy";
        string name = MftName(fb); if (name == "") name = MftName(fa);
        ushort sa = BitConverter.ToUInt16(fa, 0x10), sb = BitConverter.ToUInt16(fb, 0x10);
        bool ua = (BitConverter.ToUInt16(fa, 0x16) & 1) != 0, ub = (BitConverter.ToUInt16(fb, 0x16) & 1) != 0;
        ulong la = BitConverter.ToUInt64(fa, 8), lb = BitConverter.ToUInt64(fb, 8);
        string why;
        if (sa != sb) why = "record reused for another file";
        else if (ua != ub) why = ub ? "file created" : "file deleted";
        else if (la != lb) why = "record updated (LSN advanced)";
        else why = "changed without a new LSN";
        string where = DiffersIn(fa, fb);
        // NTFS updates some $STANDARD_INFORMATION fields (times, sizes) without logging them
        if (why == "changed without a new LSN" && where == "$STANDARD_INFORMATION") why = "$STANDARD_INFORMATION updated without a new LSN";
        return why + "; in=" + where + "; name=" + name
            + "; LSN " + Trio(la, lb, fc == null ? null : (object)BitConverter.ToUInt64(fc, 8), true)
            + "; seq " + Trio(sa, sb, fc == null ? null : (object)BitConverter.ToUInt16(fc, 0x10), false)
            + "; in use " + Trio(ua, ub, fc == null ? null : (object)((BitConverter.ToUInt16(fc, 0x16) & 1) != 0), false);
    }
}
'@

Remove-Item -Recurse -Force $Work, $Report -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $Work, $Report | Out-Null

$Search = "C:\ProgramData\Microsoft\Search\Data\Applications\Windows"
# Name: output file name. Record: read by MFT record number (RawCopy takes <volume>:<n>).
# Kind: how a differing block is decoded. Block: the unit compared.
$Checks = @(
    @{ Path = 'C:\$MFT'; Record = 0; Name = '$MFT'; Kind = "mft" },
    @{ Path = 'C:\$LogFile'; Record = 2; Name = '$LogFile'; Kind = "logfile"; Block = 4096 },
    @{ Path = 'C:\$Extend\$UsnJrnl:$J'; Name = '$J' },
    @{ Path = "C:\Windows\System32\config\SYSTEM"; Kind = "hive" },
    @{ Path = "C:\Windows\System32\config\SOFTWARE"; Kind = "hive" },
    @{ Path = "C:\Windows\System32\config\SAM"; Kind = "hive" },
    @{ Path = "C:\Windows\System32\config\SYSTEM.LOG1" },
    @{ Path = "C:\Windows\AppCompat\Programs\Amcache.hve"; Kind = "hive" },
    @{ Path = "C:\Windows\System32\sru\SRUDB.dat" },
    @{ Path = "C:\Windows\INF\setupapi.dev.log" },
    # Shadow copies leave out the page and swap files' contents (FilesNotToSnapshot)
    @{ Path = "C:\swapfile.sys"; NoSnapshot = $true },
    @{ Path = "$env:USERPROFILE\NTUSER.DAT"; Kind = "hive" },
    # Windows 11 replaced the ESE Windows.edb with a SQLite Windows.db
    @{ Path = $(if (Test-Path "$Search\Windows.edb") { "$Search\Windows.edb" } else { "$Search\Windows.db" }) },
    @{ Path = "C:\ProgramData\Microsoft\Network\Downloader\qmgr.db" }
)

$Summary = New-Object System.Collections.Generic.List[object]
$Blocks = New-Object System.Collections.Generic.List[object]

# The copies keep the source's attributes (SYSTEM.LOG1 is hidden), which Get-Item
# and Get-FileHash skip without -Force, so sizes and hashes go through .NET
function Test-Copy { Param ($Path) return ($Path -and [IO.File]::Exists($Path)) }
function Get-Size { Param ($Path) return (New-Object IO.FileInfo $Path).Length }
function Get-Sha256 {
    Param ($Path)
    $Stream = [IO.File]::OpenRead($Path)
    try { return [BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($Stream)) }
    finally { $Stream.Dispose() }
}

function Copy-WithReader {
    Param ($Ntfs, $Check, $Out)
    $t = Get-Date
    if ($Check.ContainsKey("Record")) { [void]$Ntfs.CopyRecord($Check.Record, "", $Out, $false) }
    else { [void]$Ntfs.CopyFile($Check.Path, $Out) }
    return ((Get-Date) - $t).TotalSeconds
}

function Copy-WithRawCopy {
    Param ($Target, $Dir)
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    $t = Get-Date
    & $RawCopy "/FileNamePath:$Target" "/OutputPath:$Dir" | Out-Null
    $Out = Get-ChildItem -LiteralPath $Dir -File -Force | Select-Object -First 1
    return @{ Seconds = ((Get-Date) - $t).TotalSeconds; Path = $(if ($Out) { $Out.FullName }) }
}

function Get-WriteTime {
    Param ($Path)
    try { return (Get-Item -LiteralPath $Path -Force).LastWriteTimeUtc.ToString("o") } catch { return "" }
}

# Compares two copies and adds a summary row with the cause, and the block rows
function Add-Comparison {
    Param ($Name, $Pass, $Check, $Reader, $Reference, $ReferenceBy, $Second, $ReferenceSecond, $Times)
    $Row = [ordered]@{
        File = $Name; Pass = $Pass; Reference = $ReferenceBy
        ReaderBytes = ""; ReferenceBytes = ""; Match = ""; DifferingBlocks = ""; Changed = ""; ToolsDisagree = ""; Mismatch = ""
        BlockSize = ""; Cause = ""; ReaderSeconds = $Times.Reader; ReferenceSeconds = $Times.Reference; SecondReadSeconds = $Times.Second
        WriteTimeBefore = $Times.Before; WriteTimeAfter = $Times.After
    }
    if (Test-Copy $Reader) { $Row.ReaderBytes = Get-Size $Reader }
    if (Test-Copy $Reference) { $Row.ReferenceBytes = Get-Size $Reference }
    if ($Row.ReaderBytes -eq "" -or $Row.ReferenceBytes -eq "") {
        $Row.Cause = $Times.Error
        if (-not $Row.Cause) { $Row.Cause = $(if ($Row.ReaderBytes -eq "") { "the reader produced nothing" } else { "no reference copy ($ReferenceBy)" }) }
        if ($Row.ReaderBytes -ne "" -and (Test-Copy $Second)) {
            # No reference (the $J stream): the reader's two passes still show whether it moved
            $Same = (Get-Sha256 $Reader) -eq (Get-Sha256 $Second)
            $Row.Cause += $(if ($Same) { "; the reader's two passes are identical" } else { "; the reader's two passes differ (file written during the run)" })
        }
        $Summary.Add([pscustomobject]$Row); return
    }
    if ((Get-Sha256 $Reader) -eq (Get-Sha256 $Reference)) {
        $Row.Match = $true; $Row.Cause = "identical"
        $Summary.Add([pscustomobject]$Row); return
    }
    $Size = if ($Check.Block) { $Check.Block } elseif ($Check.Kind -eq "mft") { $Ntfs.RecordSize } else { 4096 }
    $Kind = if ($Check.Kind) { $Check.Kind } else { "" }
    $Total = [long]0; $Changed = [long]0
    if (-not (Test-Copy $Second)) { $Second = $null }
    if (-not (Test-Copy $ReferenceSecond)) { $ReferenceSecond = $null }
    $Rows = [RawCheckDiff]::Compare($Reader, $Reference, $Second, $ReferenceSecond, $Size, $Kind, $MaxBlockRows, [ref]$Total, [ref]$Changed)
    foreach ($b in $Rows) {
        $Blocks.Add([pscustomobject][ordered]@{ File = $Name; Pass = $Pass; Block = $b.Block; Offset = $b.Offset; Class = $b.Class; Detail = $b.Detail })
    }
    $Row.Match = $false; $Row.BlockSize = $Size
    $Row.DifferingBlocks = "{0} of {1}" -f $Total, [math]::Ceiling([math]::Max($Row.ReaderBytes, $Row.ReferenceBytes) / $Size)
    if ($Second) {
        $Row.Changed = $Changed; $Row.ToolsDisagree = $Total - $Changed
        $Reasons = $Rows | Group-Object { ($_.Detail -split ';')[0] } | Sort-Object Count -Descending |
            Where-Object { $_.Name } | Select-Object -First 3 | ForEach-Object { "$($_.Name) x$($_.Count)" }
        $Stable = @($Rows | Where-Object { $_.Class -ne "changed" })
        $Row.Cause = $(if ($Total -eq $Changed) { "live churn: every differing block also changed between one tool's two passes" }
                       elseif ($Total - $Changed -eq $Stable.Count -and @($Stable | Where-Object { $_.Detail -notlike "past the valid data length*" }).Count -eq 0) {
                           "$($Total - $Changed) block(s) past the file's valid data length: the reader returns zeros there as Windows does, RawCopy copies the stale clusters" }
                       else { "$($Total - $Changed) block(s) stable in both tools' passes but different between the tools: one reads them wrongly (see the snapshot row)" })
        if ($Times.Before -and $Times.Before -ne $Times.After) { $Row.Cause += "; LastWriteTime moved during the run" }
        if ($Reasons) { $Row.Cause += " (" + ($Reasons -join ", ") + ")" }
    }
    else {
        $Row.Mismatch = $Total
        $Row.Cause = "READER FAULT: copies of one frozen snapshot differ"
    }
    if ($Row.ReaderBytes -ne $Row.ReferenceBytes) { $Row.Cause += "; sizes differ" }
    $Summary.Add([pscustomobject]$Row)
}

$RunStarted = Get-Date
$Os = Get-CimInstance Win32_OperatingSystem
$Ntfs = New-Object GandalfNtfs("C:")
$OpenSeconds = ((Get-Date) - $RunStarted).TotalSeconds
Write-Output ("# reader opened C: in {0:N1}s (cluster {1}, record {2})" -f $OpenSeconds, $Ntfs.ClusterSize, $Ntfs.RecordSize)

# Live: reader, RawCopy, reader again
foreach ($Check in $Checks) {
    $Name = if ($Check.Name) { $Check.Name } else { Split-Path -Leaf $Check.Path }
    $Dir = Join-Path $Work "live"; New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    $Reader = Join-Path $Dir "$Name.reader"; $Second = Join-Path $Dir "$Name.reader2"; $Reference = $null
    $Times = @{ Reader = ""; Reference = ""; Second = ""; Before = ""; After = ""; Error = "" }
    if (-not $Check.ContainsKey("Record")) { $Times.Before = Get-WriteTime $Check.Path }
    try { $Times.Reader = "{0:N1}" -f (Copy-WithReader $Ntfs $Check $Reader) }
    catch { $Times.Error = "reader: $($_.Exception.Message)"; $Reader = $null }
    if ($Reader -and $HaveRawCopy -and $Name -ne '$J') {
        $Target = if ($Check.ContainsKey("Record")) { "C:$($Check.Record)" } else { $Check.Path }
        $r = Copy-WithRawCopy $Target (Join-Path $Dir "rawcopy")
        $Times.Reference = "{0:N1}" -f $r.Seconds
        if ($r.Path) { $Reference = Join-Path $Dir "$Name.rawcopy"; Move-Item -LiteralPath $r.Path -Destination $Reference -Force }
    }
    if ($Reader) {
        try { $Times.Second = "{0:N1}" -f (Copy-WithReader $Ntfs $Check $Second) } catch { $Second = $null }
    }
    else { $Second = $null }
    $ReferenceSecond = $null
    if ($Reference) {
        $r = Copy-WithRawCopy $Target (Join-Path $Dir "rawcopy2")
        if ($r.Path) { $ReferenceSecond = Join-Path $Dir "$Name.rawcopy2"; Move-Item -LiteralPath $r.Path -Destination $ReferenceSecond -Force }
    }
    if (-not $Check.ContainsKey("Record")) { $Times.After = Get-WriteTime $Check.Path }
    $By = if ($Name -eq '$J') { "none (RawCopy can't copy the `$J stream)" } elseif ($HaveRawCopy) { "RawCopy" } else { "none (no RawCopy)" }
    try { Add-Comparison $Name "live" $Check $Reader $Reference $By $Second $ReferenceSecond $Times }
    catch { $Summary.Add([pscustomobject][ordered]@{ File = $Name; Pass = "live"; Reference = $By; Cause = "comparison failed: $($_.Exception.Message)" }) }
    Remove-Item -Recurse -Force $Dir -ErrorAction SilentlyContinue
}
$Ntfs.Dispose()

# Snapshot: the reader and an independent copy off one VSS snapshot
$ShadowInfo = @{ Created = $false; Device = ""; Error = "" }
$Shadow = $null
try {
    $Created = (Get-WmiObject -List Win32_ShadowCopy).Create("C:\", "ClientAccessible")
    if ($Created.ReturnValue -ne 0) { throw "Win32_ShadowCopy.Create returned $($Created.ReturnValue)" }
    $Shadow = Get-WmiObject Win32_ShadowCopy | Where-Object { $_.ID -eq $Created.ShadowID }
    $ShadowInfo.Created = $true; $ShadowInfo.Device = $Shadow.DeviceObject
    # RawCopy takes \\.\HarddiskVolumeShadowCopyN:<record>, but not a path on the snapshot
    $RawCopyVolume = $Shadow.DeviceObject -replace '^\\\\\?\\GLOBALROOT\\Device\\', '\\.\'
    $Ntfs = New-Object GandalfNtfs(([RawCheckDiff]::OpenDevice($Shadow.DeviceObject)), [long]0)
    foreach ($Check in $Checks) {
        $Name = if ($Check.Name) { $Check.Name } else { Split-Path -Leaf $Check.Path }
        if ($Check.NoSnapshot) {
            $Summary.Add([pscustomobject][ordered]@{ File = $Name; Pass = "snapshot"; Reference = "none"; Cause = "not compared: shadow copies leave its contents out (FilesNotToSnapshot)" })
            continue
        }
        $Dir = Join-Path $Work "snapshot"; New-Item -ItemType Directory -Force -Path $Dir | Out-Null
        $Reader = Join-Path $Dir "$Name.reader"; $Reference = $null; $By = ""
        $Times = @{ Reader = ""; Reference = ""; Second = ""; Before = ""; After = ""; Error = "" }
        try { $Times.Reader = "{0:N1}" -f (Copy-WithReader $Ntfs $Check $Reader) }
        catch { $Times.Error = "reader: $($_.Exception.Message)"; $Reader = $null }
        if ($Reader) {
            $t = Get-Date
            if ($Check.ContainsKey("Record")) {
                $By = "RawCopy (snapshot record)"
                if ($HaveRawCopy) {
                    $r = Copy-WithRawCopy "$($RawCopyVolume):$($Check.Record)" (Join-Path $Dir "rawcopy")
                    if ($r.Path) { $Reference = Join-Path $Dir "$Name.reference"; Move-Item -LiteralPath $r.Path -Destination $Reference -Force }
                }
                else { $By = "none (no RawCopy)" }
            }
            elseif ($Name -eq '$J') { $By = "none (no other tool copies the `$J stream)" }
            else {
                $By = "Windows file copy"
                $Reference = Join-Path $Dir "$Name.reference"
                try { [IO.File]::Copy($Shadow.DeviceObject + $Check.Path.Substring(2), $Reference, $true) }
                catch { $Times.Error = "Windows copy: $($_.Exception.Message)"; $Reference = $null }
            }
            $Times.Reference = "{0:N1}" -f ((Get-Date) - $t).TotalSeconds
        }
        try { Add-Comparison $Name "snapshot" $Check $Reader $Reference $By $null $null $Times }
        catch { $Summary.Add([pscustomobject][ordered]@{ File = $Name; Pass = "snapshot"; Reference = $By; Cause = "comparison failed: $($_.Exception.Message)" }) }
        Remove-Item -Recurse -Force $Dir -ErrorAction SilentlyContinue
    }
    $Ntfs.Dispose()
}
catch { $ShadowInfo.Error = $_.Exception.Message; Write-Output "# snapshot pass skipped: $($ShadowInfo.Error)" }
finally { if ($Shadow) { $Shadow.Delete() } }

$Summary | Export-Csv -NoTypeInformation -Encoding UTF8 -LiteralPath (Join-Path $Report "summary.csv")
$Blocks | Export-Csv -NoTypeInformation -Encoding UTF8 -LiteralPath (Join-Path $Report "blocks.csv")
[ordered]@{
    started = $RunStarted.ToUniversalTime().ToString("o")
    finished = (Get-Date).ToUniversalTime().ToString("o")
    host = $env:COMPUTERNAME
    os = "$($Os.Caption) $($Os.Version) build $($Os.BuildNumber)"
    cluster_size = $Ntfs.ClusterSize; record_size = $Ntfs.RecordSize
    reader_open_seconds = [math]::Round($OpenSeconds, 1)
    rawcopy = $HaveRawCopy; snapshot = $ShadowInfo
    max_block_rows = $MaxBlockRows
    reader_faults = @($Summary | Where-Object { $_.Pass -eq "snapshot" -and $_.Match -eq $false }).Count
    tools_disagree_live_blocks = ($Summary | Where-Object { $_.ToolsDisagree } | Measure-Object -Property ToolsDisagree -Sum).Sum
} | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Report "run.json")

$Summary | Format-Table File, Pass, Reference, ReaderBytes, ReferenceBytes, Match, DifferingBlocks, Changed, ToolsDisagree, ReaderSeconds, ReferenceSeconds -AutoSize | Out-String -Width 240
$Summary | Where-Object { $_.Match -ne $true } | ForEach-Object { "{0} ({1}): {2}" -f $_.File, $_.Pass, $_.Cause }
Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue
