/*
    Rivendell Sample YARA Rules
    For testing purposes only
*/

rule Suspicious_PowerShell_Command {
    meta:
        description = "Detects suspicious PowerShell commands"
        author = "Rivendell Test"
        severity = "medium"
    strings:
        $ps1 = "powershell" nocase
        $ps2 = "-encodedcommand" nocase
        $ps3 = "-enc " nocase
        $ps4 = "bypass" nocase
        $ps5 = "hidden" nocase
    condition:
        $ps1 and any of ($ps2, $ps3, $ps4, $ps5)
}

rule Potential_Credential_Access {
    meta:
        description = "Detects potential credential access attempts"
        author = "Rivendell Test"
        severity = "high"
    strings:
        $s1 = "mimikatz" nocase
        $s2 = "sekurlsa" nocase
        $s3 = "lsadump" nocase
        $s4 = "kerberos::golden" nocase
        $s5 = "privilege::debug" nocase
    condition:
        any of them
}

rule Suspicious_Network_Activity {
    meta:
        description = "Detects suspicious network-related strings"
        author = "Rivendell Test"
        severity = "medium"
    strings:
        $n1 = "wget http" nocase
        $n2 = "curl http" nocase
        $n3 = "Invoke-WebRequest" nocase
        $n4 = "Net.WebClient" nocase
        $n5 = "DownloadString" nocase
        $n6 = "DownloadFile" nocase
    condition:
        any of them
}

rule Base64_Encoded_Content {
    meta:
        description = "Detects base64 encoded executable content"
        author = "Rivendell Test"
        severity = "low"
    strings:
        $mz = "TVqQAAMAAAA"  // Base64 MZ header
        $pe = "UEsDBA"       // Base64 PK (ZIP) header
    condition:
        any of them
}

rule Persistence_Registry_Keys {
    meta:
        description = "Detects references to common persistence registry keys"
        author = "Rivendell Test"
        severity = "medium"
    strings:
        $r1 = "CurrentVersion\\Run" nocase
        $r2 = "CurrentVersion\\RunOnce" nocase
        $r3 = "Winlogon\\Shell" nocase
        $r4 = "Winlogon\\Userinit" nocase
        $r5 = "CurrentVersion\\Policies\\Explorer\\Run" nocase
    condition:
        any of them
}
