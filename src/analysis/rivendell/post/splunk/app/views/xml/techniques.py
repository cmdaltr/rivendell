#!/usr/bin/env python3
"""
MITRE ATT&CK Technique Dashboard Generator for Splunk

This module generates individual XML dashboard views for each MITRE ATT&CK technique.
The dashboards provide detailed views of events mapped to specific techniques.
Updated for MITRE ATT&CK v18.1 with comprehensive technique coverage.
"""

# Complete technique definitions organized by tactic
# Format: {technique_id: (name, tactic, description)}
# Includes parent techniques and major sub-techniques

TECHNIQUES = {
    # ==================== RECONNAISSANCE ====================
    "T1595": ("Active Scanning", "Reconnaissance", "Adversaries may execute active reconnaissance scans to gather information."),
    "T1595.001": ("Scanning IP Blocks", "Reconnaissance", "Adversaries may scan IP blocks to gather victim network information."),
    "T1595.002": ("Vulnerability Scanning", "Reconnaissance", "Adversaries may scan for vulnerabilities in victim systems."),
    "T1595.003": ("Wordlist Scanning", "Reconnaissance", "Adversaries may use wordlist scanning to identify valid resources."),
    "T1592": ("Gather Victim Host Information", "Reconnaissance", "Adversaries may gather information about victim hosts."),
    "T1592.001": ("Hardware", "Reconnaissance", "Adversaries may gather hardware information about victims."),
    "T1592.002": ("Software", "Reconnaissance", "Adversaries may gather software information about victims."),
    "T1592.003": ("Firmware", "Reconnaissance", "Adversaries may gather firmware information about victims."),
    "T1592.004": ("Client Configurations", "Reconnaissance", "Adversaries may gather client configuration information."),
    "T1589": ("Gather Victim Identity Information", "Reconnaissance", "Adversaries may gather identity information about victims."),
    "T1589.001": ("Credentials", "Reconnaissance", "Adversaries may gather credentials of victims."),
    "T1589.002": ("Email Addresses", "Reconnaissance", "Adversaries may gather email addresses of victims."),
    "T1589.003": ("Employee Names", "Reconnaissance", "Adversaries may gather employee names from victims."),
    "T1590": ("Gather Victim Network Information", "Reconnaissance", "Adversaries may gather network information about victims."),
    "T1590.001": ("Domain Properties", "Reconnaissance", "Adversaries may gather domain property information."),
    "T1590.002": ("DNS", "Reconnaissance", "Adversaries may gather DNS information about victims."),
    "T1590.003": ("Network Trust Dependencies", "Reconnaissance", "Adversaries may gather network trust information."),
    "T1590.004": ("Network Topology", "Reconnaissance", "Adversaries may gather network topology information."),
    "T1590.005": ("IP Addresses", "Reconnaissance", "Adversaries may gather IP address information."),
    "T1590.006": ("Network Security Appliances", "Reconnaissance", "Adversaries may gather security appliance information."),
    "T1591": ("Gather Victim Org Information", "Reconnaissance", "Adversaries may gather organizational information."),
    "T1591.001": ("Determine Physical Locations", "Reconnaissance", "Adversaries may determine physical locations of victims."),
    "T1591.002": ("Business Relationships", "Reconnaissance", "Adversaries may gather business relationship information."),
    "T1591.003": ("Identify Business Tempo", "Reconnaissance", "Adversaries may identify business tempo of victims."),
    "T1591.004": ("Identify Roles", "Reconnaissance", "Adversaries may identify roles within victim organizations."),
    "T1598": ("Phishing for Information", "Reconnaissance", "Adversaries may send phishing messages to gather information."),
    "T1598.001": ("Spearphishing Service", "Reconnaissance", "Adversaries may use spearphishing via third-party services."),
    "T1598.002": ("Spearphishing Attachment", "Reconnaissance", "Adversaries may use spearphishing with attachments for info."),
    "T1598.003": ("Spearphishing Link", "Reconnaissance", "Adversaries may use spearphishing links to gather info."),
    "T1597": ("Search Closed Sources", "Reconnaissance", "Adversaries may search closed sources for victim information."),
    "T1597.001": ("Threat Intel Vendors", "Reconnaissance", "Adversaries may search threat intel vendor data."),
    "T1597.002": ("Purchase Technical Data", "Reconnaissance", "Adversaries may purchase technical data about victims."),
    "T1596": ("Search Open Technical Databases", "Reconnaissance", "Adversaries may search open technical databases."),
    "T1596.001": ("DNS/Passive DNS", "Reconnaissance", "Adversaries may search DNS/passive DNS data."),
    "T1596.002": ("WHOIS", "Reconnaissance", "Adversaries may search WHOIS data."),
    "T1596.003": ("Digital Certificates", "Reconnaissance", "Adversaries may search digital certificate data."),
    "T1596.004": ("CDNs", "Reconnaissance", "Adversaries may search CDN data."),
    "T1596.005": ("Scan Databases", "Reconnaissance", "Adversaries may search scan databases."),
    "T1593": ("Search Open Websites/Domains", "Reconnaissance", "Adversaries may search open websites for victim info."),
    "T1593.001": ("Social Media", "Reconnaissance", "Adversaries may search social media for victim info."),
    "T1593.002": ("Search Engines", "Reconnaissance", "Adversaries may use search engines for victim info."),
    "T1593.003": ("Code Repositories", "Reconnaissance", "Adversaries may search code repositories."),
    "T1594": ("Search Victim-Owned Websites", "Reconnaissance", "Adversaries may search victim-owned websites."),

    # ==================== RESOURCE DEVELOPMENT ====================
    "T1583": ("Acquire Infrastructure", "Resource Development", "Adversaries may acquire infrastructure for operations."),
    "T1583.001": ("Domains", "Resource Development", "Adversaries may acquire domains for operations."),
    "T1583.002": ("DNS Server", "Resource Development", "Adversaries may set up DNS servers."),
    "T1583.003": ("Virtual Private Server", "Resource Development", "Adversaries may acquire VPS for operations."),
    "T1583.004": ("Server", "Resource Development", "Adversaries may acquire servers for operations."),
    "T1583.005": ("Botnet", "Resource Development", "Adversaries may acquire access to botnets."),
    "T1583.006": ("Web Services", "Resource Development", "Adversaries may acquire web services."),
    "T1583.007": ("Serverless", "Resource Development", "Adversaries may acquire serverless infrastructure."),
    "T1583.008": ("Malvertising", "Resource Development", "Adversaries may use malvertising."),
    "T1586": ("Compromise Accounts", "Resource Development", "Adversaries may compromise accounts for operations."),
    "T1586.001": ("Social Media Accounts", "Resource Development", "Adversaries may compromise social media accounts."),
    "T1586.002": ("Email Accounts", "Resource Development", "Adversaries may compromise email accounts."),
    "T1586.003": ("Cloud Accounts", "Resource Development", "Adversaries may compromise cloud accounts."),
    "T1584": ("Compromise Infrastructure", "Resource Development", "Adversaries may compromise infrastructure."),
    "T1584.001": ("Domains", "Resource Development", "Adversaries may compromise domains."),
    "T1584.002": ("DNS Server", "Resource Development", "Adversaries may compromise DNS servers."),
    "T1584.003": ("Virtual Private Server", "Resource Development", "Adversaries may compromise VPS."),
    "T1584.004": ("Server", "Resource Development", "Adversaries may compromise servers."),
    "T1584.005": ("Botnet", "Resource Development", "Adversaries may compromise botnets."),
    "T1584.006": ("Web Services", "Resource Development", "Adversaries may compromise web services."),
    "T1584.007": ("Serverless", "Resource Development", "Adversaries may compromise serverless infrastructure."),
    "T1587": ("Develop Capabilities", "Resource Development", "Adversaries may develop capabilities."),
    "T1587.001": ("Malware", "Resource Development", "Adversaries may develop malware."),
    "T1587.002": ("Code Signing Certificates", "Resource Development", "Adversaries may develop code signing certs."),
    "T1587.003": ("Digital Certificates", "Resource Development", "Adversaries may develop digital certificates."),
    "T1587.004": ("Exploits", "Resource Development", "Adversaries may develop exploits."),
    "T1585": ("Establish Accounts", "Resource Development", "Adversaries may establish accounts."),
    "T1585.001": ("Social Media Accounts", "Resource Development", "Adversaries may establish social media accounts."),
    "T1585.002": ("Email Accounts", "Resource Development", "Adversaries may establish email accounts."),
    "T1585.003": ("Cloud Accounts", "Resource Development", "Adversaries may establish cloud accounts."),
    "T1588": ("Obtain Capabilities", "Resource Development", "Adversaries may obtain capabilities."),
    "T1588.001": ("Malware", "Resource Development", "Adversaries may obtain malware."),
    "T1588.002": ("Tool", "Resource Development", "Adversaries may obtain tools."),
    "T1588.003": ("Code Signing Certificates", "Resource Development", "Adversaries may obtain code signing certs."),
    "T1588.004": ("Digital Certificates", "Resource Development", "Adversaries may obtain digital certificates."),
    "T1588.005": ("Exploits", "Resource Development", "Adversaries may obtain exploits."),
    "T1588.006": ("Vulnerabilities", "Resource Development", "Adversaries may obtain vulnerability information."),
    "T1608": ("Stage Capabilities", "Resource Development", "Adversaries may stage capabilities."),
    "T1608.001": ("Upload Malware", "Resource Development", "Adversaries may upload malware."),
    "T1608.002": ("Upload Tool", "Resource Development", "Adversaries may upload tools."),
    "T1608.003": ("Install Digital Certificate", "Resource Development", "Adversaries may install digital certificates."),
    "T1608.004": ("Drive-by Target", "Resource Development", "Adversaries may stage drive-by targets."),
    "T1608.005": ("Link Target", "Resource Development", "Adversaries may stage link targets."),
    "T1608.006": ("SEO Poisoning", "Resource Development", "Adversaries may use SEO poisoning."),

    # ==================== INITIAL ACCESS ====================
    "T1659": ("Content Injection", "Initial Access", "Adversaries may inject malicious content into systems through online network traffic."),
    "T1189": ("Drive-by Compromise", "Initial Access", "Adversaries may gain access through a user visiting a website during normal browsing."),
    "T1190": ("Exploit Public-Facing Application", "Initial Access", "Adversaries may exploit vulnerabilities in Internet-facing computer systems."),
    "T1133": ("External Remote Services", "Initial Access", "Adversaries may leverage external-facing remote services to access a network."),
    "T1200": ("Hardware Additions", "Initial Access", "Adversaries may introduce computer accessories or hardware to gain access."),
    "T1566": ("Phishing", "Initial Access", "Adversaries may send phishing messages to gain access to victim systems."),
    "T1566.001": ("Spearphishing Attachment", "Initial Access", "Adversaries may send spearphishing with malicious attachments."),
    "T1566.002": ("Spearphishing Link", "Initial Access", "Adversaries may send spearphishing with malicious links."),
    "T1566.003": ("Spearphishing via Service", "Initial Access", "Adversaries may send spearphishing via third-party services."),
    "T1566.004": ("Spearphishing Voice", "Initial Access", "Adversaries may use voice phishing (vishing)."),
    "T1091": ("Replication Through Removable Media", "Initial Access", "Adversaries may move onto systems via removable media."),
    "T1195": ("Supply Chain Compromise", "Initial Access", "Adversaries may manipulate products or mechanisms prior to receipt."),
    "T1195.001": ("Compromise Software Dependencies", "Initial Access", "Adversaries may compromise software dependencies."),
    "T1195.002": ("Compromise Software Supply Chain", "Initial Access", "Adversaries may compromise the software supply chain."),
    "T1195.003": ("Compromise Hardware Supply Chain", "Initial Access", "Adversaries may compromise the hardware supply chain."),
    "T1199": ("Trusted Relationship", "Initial Access", "Adversaries may breach organizations via trusted third party relationships."),
    "T1078": ("Valid Accounts", "Initial Access", "Adversaries may use credentials of existing accounts to gain access."),
    "T1078.001": ("Default Accounts", "Initial Access", "Adversaries may use default accounts."),
    "T1078.002": ("Domain Accounts", "Initial Access", "Adversaries may use domain accounts."),
    "T1078.003": ("Local Accounts", "Initial Access", "Adversaries may use local accounts."),
    "T1078.004": ("Cloud Accounts", "Initial Access", "Adversaries may use cloud accounts."),

    # ==================== EXECUTION ====================
    "T1651": ("Cloud Administration Command", "Execution", "Adversaries may abuse cloud management services to execute commands."),
    "T1059": ("Command and Scripting Interpreter", "Execution", "Adversaries may abuse command and script interpreters to execute commands."),
    "T1059.001": ("PowerShell", "Execution", "Adversaries may abuse PowerShell for execution."),
    "T1059.002": ("AppleScript", "Execution", "Adversaries may abuse AppleScript for execution."),
    "T1059.003": ("Windows Command Shell", "Execution", "Adversaries may abuse Windows Command Shell."),
    "T1059.004": ("Unix Shell", "Execution", "Adversaries may abuse Unix shells for execution."),
    "T1059.005": ("Visual Basic", "Execution", "Adversaries may abuse Visual Basic for execution."),
    "T1059.006": ("Python", "Execution", "Adversaries may abuse Python for execution."),
    "T1059.007": ("JavaScript", "Execution", "Adversaries may abuse JavaScript for execution."),
    "T1059.008": ("Network Device CLI", "Execution", "Adversaries may abuse network device CLIs."),
    "T1059.009": ("Cloud API", "Execution", "Adversaries may abuse cloud APIs for execution."),
    "T1609": ("Container Administration Command", "Execution", "Adversaries may abuse a container administration service to execute commands."),
    "T1610": ("Deploy Container", "Execution", "Adversaries may deploy a container into an environment to facilitate execution."),
    "T1203": ("Exploitation for Client Execution", "Execution", "Adversaries may exploit software vulnerabilities in client applications."),
    "T1559": ("Inter-Process Communication", "Execution", "Adversaries may abuse inter-process communication mechanisms for execution."),
    "T1559.001": ("Component Object Model", "Execution", "Adversaries may abuse COM for execution."),
    "T1559.002": ("Dynamic Data Exchange", "Execution", "Adversaries may abuse DDE for execution."),
    "T1559.003": ("XPC Services", "Execution", "Adversaries may abuse XPC services for execution."),
    "T1106": ("Native API", "Execution", "Adversaries may interact with the native OS API to execute behaviors."),
    "T1053": ("Scheduled Task/Job", "Execution", "Adversaries may abuse task scheduling functionality to execute malicious code."),
    "T1053.001": ("At", "Execution", "Adversaries may abuse the at utility."),
    "T1053.002": ("At (Windows)", "Execution", "Adversaries may abuse at on Windows."),
    "T1053.003": ("Cron", "Execution", "Adversaries may abuse cron for execution."),
    "T1053.005": ("Scheduled Task", "Execution", "Adversaries may abuse Windows Task Scheduler."),
    "T1053.006": ("Systemd Timers", "Execution", "Adversaries may abuse systemd timers."),
    "T1053.007": ("Container Orchestration Job", "Execution", "Adversaries may abuse container orchestration jobs."),
    "T1129": ("Shared Modules", "Execution", "Adversaries may execute malicious payloads via loading shared modules."),
    "T1072": ("Software Deployment Tools", "Execution", "Adversaries may gain access to third-party software deployment tools."),
    "T1569": ("System Services", "Execution", "Adversaries may abuse system services or daemons to execute commands."),
    "T1569.001": ("Launchctl", "Execution", "Adversaries may abuse launchctl."),
    "T1569.002": ("Service Execution", "Execution", "Adversaries may abuse Windows services."),
    "T1204": ("User Execution", "Execution", "Adversaries may rely on specific actions by a user for execution."),
    "T1204.001": ("Malicious Link", "Execution", "Adversaries may rely on users clicking malicious links."),
    "T1204.002": ("Malicious File", "Execution", "Adversaries may rely on users opening malicious files."),
    "T1204.003": ("Malicious Image", "Execution", "Adversaries may rely on users running malicious images."),
    "T1047": ("Windows Management Instrumentation", "Execution", "Adversaries may abuse WMI to execute malicious commands and payloads."),

    # ==================== PERSISTENCE ====================
    "T1098": ("Account Manipulation", "Persistence", "Adversaries may manipulate accounts to maintain access to victim systems."),
    "T1098.001": ("Additional Cloud Credentials", "Persistence", "Adversaries may add additional cloud credentials."),
    "T1098.002": ("Additional Email Delegate Permissions", "Persistence", "Adversaries may add email delegate permissions."),
    "T1098.003": ("Additional Cloud Roles", "Persistence", "Adversaries may add additional cloud roles."),
    "T1098.004": ("SSH Authorized Keys", "Persistence", "Adversaries may modify SSH authorized keys."),
    "T1098.005": ("Device Registration", "Persistence", "Adversaries may register devices."),
    "T1098.006": ("Additional Container Cluster Roles", "Persistence", "Adversaries may add container cluster roles."),
    "T1197": ("BITS Jobs", "Persistence", "Adversaries may abuse BITS jobs to persistently execute code."),
    "T1547": ("Boot or Logon Autostart Execution", "Persistence", "Adversaries may configure system settings to automatically execute a program."),
    "T1547.001": ("Registry Run Keys / Startup Folder", "Persistence", "Adversaries may use registry run keys or startup folder."),
    "T1547.002": ("Authentication Package", "Persistence", "Adversaries may abuse authentication packages."),
    "T1547.003": ("Time Providers", "Persistence", "Adversaries may abuse time providers."),
    "T1547.004": ("Winlogon Helper DLL", "Persistence", "Adversaries may abuse Winlogon helper DLLs."),
    "T1547.005": ("Security Support Provider", "Persistence", "Adversaries may abuse SSPs."),
    "T1547.006": ("Kernel Modules and Extensions", "Persistence", "Adversaries may abuse kernel modules."),
    "T1547.007": ("Re-opened Applications", "Persistence", "Adversaries may abuse re-opened applications."),
    "T1547.008": ("LSASS Driver", "Persistence", "Adversaries may abuse LSASS drivers."),
    "T1547.009": ("Shortcut Modification", "Persistence", "Adversaries may modify shortcuts."),
    "T1547.010": ("Port Monitors", "Persistence", "Adversaries may abuse port monitors."),
    "T1547.012": ("Print Processors", "Persistence", "Adversaries may abuse print processors."),
    "T1547.013": ("XDG Autostart Entries", "Persistence", "Adversaries may abuse XDG autostart."),
    "T1547.014": ("Active Setup", "Persistence", "Adversaries may abuse Active Setup."),
    "T1547.015": ("Login Items", "Persistence", "Adversaries may abuse login items."),
    "T1037": ("Boot or Logon Initialization Scripts", "Persistence", "Adversaries may use scripts automatically executed at boot or logon."),
    "T1037.001": ("Logon Script (Windows)", "Persistence", "Adversaries may use Windows logon scripts."),
    "T1037.002": ("Login Hook", "Persistence", "Adversaries may use login hooks."),
    "T1037.003": ("Network Logon Script", "Persistence", "Adversaries may use network logon scripts."),
    "T1037.004": ("RC Scripts", "Persistence", "Adversaries may use RC scripts."),
    "T1037.005": ("Startup Items", "Persistence", "Adversaries may use startup items."),
    "T1176": ("Browser Extensions", "Persistence", "Adversaries may abuse browser extensions to establish persistent access."),
    "T1554": ("Compromise Client Software Binary", "Persistence", "Adversaries may modify client software binaries to establish persistent access."),
    "T1136": ("Create Account", "Persistence", "Adversaries may create an account to maintain access to victim systems."),
    "T1136.001": ("Local Account", "Persistence", "Adversaries may create local accounts."),
    "T1136.002": ("Domain Account", "Persistence", "Adversaries may create domain accounts."),
    "T1136.003": ("Cloud Account", "Persistence", "Adversaries may create cloud accounts."),
    "T1543": ("Create or Modify System Process", "Persistence", "Adversaries may create or modify system-level processes to execute payloads."),
    "T1543.001": ("Launch Agent", "Persistence", "Adversaries may create launch agents."),
    "T1543.002": ("Systemd Service", "Persistence", "Adversaries may create systemd services."),
    "T1543.003": ("Windows Service", "Persistence", "Adversaries may create Windows services."),
    "T1543.004": ("Launch Daemon", "Persistence", "Adversaries may create launch daemons."),
    "T1546": ("Event Triggered Execution", "Persistence", "Adversaries may establish persistence using system mechanisms that trigger execution."),
    "T1546.001": ("Change Default File Association", "Persistence", "Adversaries may change file associations."),
    "T1546.002": ("Screensaver", "Persistence", "Adversaries may abuse screensavers."),
    "T1546.003": ("Windows Management Instrumentation Event Subscription", "Persistence", "Adversaries may use WMI event subscriptions."),
    "T1546.004": ("Unix Shell Configuration Modification", "Persistence", "Adversaries may modify Unix shell configs."),
    "T1546.005": ("Trap", "Persistence", "Adversaries may use trap commands."),
    "T1546.006": ("LC_LOAD_DYLIB Addition", "Persistence", "Adversaries may add LC_LOAD_DYLIB."),
    "T1546.007": ("Netsh Helper DLL", "Persistence", "Adversaries may use Netsh helper DLLs."),
    "T1546.008": ("Accessibility Features", "Persistence", "Adversaries may abuse accessibility features."),
    "T1546.009": ("AppCert DLLs", "Persistence", "Adversaries may use AppCert DLLs."),
    "T1546.010": ("AppInit DLLs", "Persistence", "Adversaries may use AppInit DLLs."),
    "T1546.011": ("Application Shimming", "Persistence", "Adversaries may use application shimming."),
    "T1546.012": ("Image File Execution Options Injection", "Persistence", "Adversaries may use IFEO injection."),
    "T1546.013": ("PowerShell Profile", "Persistence", "Adversaries may modify PowerShell profiles."),
    "T1546.014": ("Emond", "Persistence", "Adversaries may abuse emond."),
    "T1546.015": ("Component Object Model Hijacking", "Persistence", "Adversaries may hijack COM objects."),
    "T1546.016": ("Installer Packages", "Persistence", "Adversaries may abuse installer packages."),
    "T1574": ("Hijack Execution Flow", "Persistence", "Adversaries may execute their own malicious payloads by hijacking execution flow."),
    "T1574.001": ("DLL Search Order Hijacking", "Persistence", "Adversaries may hijack DLL search order."),
    "T1574.002": ("DLL Side-Loading", "Persistence", "Adversaries may side-load DLLs."),
    "T1574.004": ("Dylib Hijacking", "Persistence", "Adversaries may hijack dylibs."),
    "T1574.005": ("Executable Installer File Permissions Weakness", "Persistence", "Adversaries may abuse installer file permissions."),
    "T1574.006": ("Dynamic Linker Hijacking", "Persistence", "Adversaries may hijack dynamic linkers."),
    "T1574.007": ("Path Interception by PATH Environment Variable", "Persistence", "Adversaries may use PATH interception."),
    "T1574.008": ("Path Interception by Search Order Hijacking", "Persistence", "Adversaries may use search order hijacking."),
    "T1574.009": ("Path Interception by Unquoted Path", "Persistence", "Adversaries may use unquoted path interception."),
    "T1574.010": ("Services File Permissions Weakness", "Persistence", "Adversaries may abuse service file permissions."),
    "T1574.011": ("Services Registry Permissions Weakness", "Persistence", "Adversaries may abuse service registry permissions."),
    "T1574.012": ("COR_PROFILER", "Persistence", "Adversaries may abuse COR_PROFILER."),
    "T1574.013": ("KernelCallbackTable", "Persistence", "Adversaries may abuse KernelCallbackTable."),
    "T1574.014": ("AppDomainManager", "Persistence", "Adversaries may abuse AppDomainManager."),
    "T1525": ("Implant Internal Image", "Persistence", "Adversaries may implant cloud or container images with malicious code."),
    "T1556": ("Modify Authentication Process", "Persistence", "Adversaries may modify authentication mechanisms to access user credentials."),
    "T1556.001": ("Domain Controller Authentication", "Persistence", "Adversaries may modify DC authentication."),
    "T1556.002": ("Password Filter DLL", "Persistence", "Adversaries may use password filter DLLs."),
    "T1556.003": ("Pluggable Authentication Modules", "Persistence", "Adversaries may modify PAM."),
    "T1556.004": ("Network Device Authentication", "Persistence", "Adversaries may modify network device auth."),
    "T1556.005": ("Reversible Encryption", "Persistence", "Adversaries may enable reversible encryption."),
    "T1556.006": ("Multi-Factor Authentication", "Persistence", "Adversaries may modify MFA."),
    "T1556.007": ("Hybrid Identity", "Persistence", "Adversaries may abuse hybrid identity."),
    "T1556.008": ("Network Provider DLL", "Persistence", "Adversaries may use Network Provider DLLs."),
    "T1137": ("Office Application Startup", "Persistence", "Adversaries may leverage Office-based applications for persistence."),
    "T1137.001": ("Office Template Macros", "Persistence", "Adversaries may use Office template macros."),
    "T1137.002": ("Office Test", "Persistence", "Adversaries may abuse Office Test registry key."),
    "T1137.003": ("Outlook Forms", "Persistence", "Adversaries may abuse Outlook forms."),
    "T1137.004": ("Outlook Home Page", "Persistence", "Adversaries may abuse Outlook home page."),
    "T1137.005": ("Outlook Rules", "Persistence", "Adversaries may abuse Outlook rules."),
    "T1137.006": ("Add-ins", "Persistence", "Adversaries may abuse Office add-ins."),
    "T1653": ("Power Settings", "Persistence", "Adversaries may impair power management to maintain access."),
    "T1542": ("Pre-OS Boot", "Persistence", "Adversaries may abuse Pre-OS Boot mechanisms for persistence."),
    "T1542.001": ("System Firmware", "Persistence", "Adversaries may modify system firmware."),
    "T1542.002": ("Component Firmware", "Persistence", "Adversaries may modify component firmware."),
    "T1542.003": ("Bootkit", "Persistence", "Adversaries may use bootkits."),
    "T1542.004": ("ROMMONkit", "Persistence", "Adversaries may use ROMMONkits."),
    "T1542.005": ("TFTP Boot", "Persistence", "Adversaries may abuse TFTP boot."),
    "T1505": ("Server Software Component", "Persistence", "Adversaries may abuse legitimate server software components for persistence."),
    "T1505.001": ("SQL Stored Procedures", "Persistence", "Adversaries may use SQL stored procedures."),
    "T1505.002": ("Transport Agent", "Persistence", "Adversaries may use transport agents."),
    "T1505.003": ("Web Shell", "Persistence", "Adversaries may use web shells."),
    "T1505.004": ("IIS Components", "Persistence", "Adversaries may abuse IIS components."),
    "T1505.005": ("Terminal Services DLL", "Persistence", "Adversaries may abuse Terminal Services DLLs."),
    "T1205": ("Traffic Signaling", "Persistence", "Adversaries may use traffic signaling to hide open ports or other malicious functionality."),
    "T1205.001": ("Port Knocking", "Persistence", "Adversaries may use port knocking."),
    "T1205.002": ("Socket Filters", "Persistence", "Adversaries may use socket filters."),

    # ==================== PRIVILEGE ESCALATION ====================
    "T1548": ("Abuse Elevation Control Mechanism", "Privilege Escalation", "Adversaries may circumvent mechanisms designed to control elevate privileges."),
    "T1548.001": ("Setuid and Setgid", "Privilege Escalation", "Adversaries may abuse setuid/setgid."),
    "T1548.002": ("Bypass User Account Control", "Privilege Escalation", "Adversaries may bypass UAC."),
    "T1548.003": ("Sudo and Sudo Caching", "Privilege Escalation", "Adversaries may abuse sudo."),
    "T1548.004": ("Elevated Execution with Prompt", "Privilege Escalation", "Adversaries may abuse elevation prompts."),
    "T1548.005": ("Temporary Elevated Cloud Access", "Privilege Escalation", "Adversaries may abuse temporary cloud access."),
    "T1134": ("Access Token Manipulation", "Privilege Escalation", "Adversaries may modify access tokens to operate under a different user/system security context."),
    "T1134.001": ("Token Impersonation/Theft", "Privilege Escalation", "Adversaries may impersonate/steal tokens."),
    "T1134.002": ("Create Process with Token", "Privilege Escalation", "Adversaries may create processes with tokens."),
    "T1134.003": ("Make and Impersonate Token", "Privilege Escalation", "Adversaries may make and impersonate tokens."),
    "T1134.004": ("Parent PID Spoofing", "Privilege Escalation", "Adversaries may spoof parent PID."),
    "T1134.005": ("SID-History Injection", "Privilege Escalation", "Adversaries may inject SID-History."),
    "T1484": ("Domain Policy Modification", "Privilege Escalation", "Adversaries may modify the configuration settings of a domain to evade defenses."),
    "T1484.001": ("Group Policy Modification", "Privilege Escalation", "Adversaries may modify Group Policy."),
    "T1484.002": ("Domain Trust Modification", "Privilege Escalation", "Adversaries may modify domain trusts."),
    "T1611": ("Escape to Host", "Privilege Escalation", "Adversaries may break out of a container to gain access to the underlying host."),
    "T1068": ("Exploitation for Privilege Escalation", "Privilege Escalation", "Adversaries may exploit software vulnerabilities to elevate privileges."),
    "T1055": ("Process Injection", "Privilege Escalation", "Adversaries may inject code into processes to evade defenses and elevate privileges."),
    "T1055.001": ("Dynamic-link Library Injection", "Privilege Escalation", "Adversaries may inject DLLs."),
    "T1055.002": ("Portable Executable Injection", "Privilege Escalation", "Adversaries may inject PEs."),
    "T1055.003": ("Thread Execution Hijacking", "Privilege Escalation", "Adversaries may hijack thread execution."),
    "T1055.004": ("Asynchronous Procedure Call", "Privilege Escalation", "Adversaries may use APC injection."),
    "T1055.005": ("Thread Local Storage", "Privilege Escalation", "Adversaries may use TLS injection."),
    "T1055.008": ("Ptrace System Calls", "Privilege Escalation", "Adversaries may use ptrace."),
    "T1055.009": ("Proc Memory", "Privilege Escalation", "Adversaries may inject via /proc/*/mem."),
    "T1055.011": ("Extra Window Memory Injection", "Privilege Escalation", "Adversaries may use EWM injection."),
    "T1055.012": ("Process Hollowing", "Privilege Escalation", "Adversaries may use process hollowing."),
    "T1055.013": ("Process Doppelgänging", "Privilege Escalation", "Adversaries may use process doppelgänging."),
    "T1055.014": ("VDSO Hijacking", "Privilege Escalation", "Adversaries may hijack VDSO."),
    "T1055.015": ("ListPlanting", "Privilege Escalation", "Adversaries may use ListPlanting."),

    # ==================== DEFENSE EVASION ====================
    "T1612": ("Build Image on Host", "Defense Evasion", "Adversaries may build a container image directly on a host to bypass defenses."),
    "T1622": ("Debugger Evasion", "Defense Evasion", "Adversaries may employ means to detect and avoid debuggers."),
    "T1140": ("Deobfuscate/Decode Files or Information", "Defense Evasion", "Adversaries may use obfuscation to hide files and artifacts."),
    "T1610": ("Deploy Container", "Defense Evasion", "Adversaries may deploy containers to evade defenses."),
    "T1006": ("Direct Volume Access", "Defense Evasion", "Adversaries may directly access a volume to bypass file access controls."),
    "T1484": ("Domain Policy Modification", "Defense Evasion", "Adversaries may modify domain policies."),
    "T1480": ("Execution Guardrails", "Defense Evasion", "Adversaries may use execution guardrails to constrain execution environment."),
    "T1480.001": ("Environmental Keying", "Defense Evasion", "Adversaries may use environmental keying."),
    "T1211": ("Exploitation for Defense Evasion", "Defense Evasion", "Adversaries may exploit vulnerabilities to evade defenses."),
    "T1222": ("File and Directory Permissions Modification", "Defense Evasion", "Adversaries may modify file or directory permissions."),
    "T1222.001": ("Windows File and Directory Permissions Modification", "Defense Evasion", "Windows permissions modification."),
    "T1222.002": ("Linux and Mac File and Directory Permissions Modification", "Defense Evasion", "Linux/Mac permissions modification."),
    "T1564": ("Hide Artifacts", "Defense Evasion", "Adversaries may attempt to hide artifacts to evade detection."),
    "T1564.001": ("Hidden Files and Directories", "Defense Evasion", "Adversaries may hide files/directories."),
    "T1564.002": ("Hidden Users", "Defense Evasion", "Adversaries may hide users."),
    "T1564.003": ("Hidden Window", "Defense Evasion", "Adversaries may hide windows."),
    "T1564.004": ("NTFS File Attributes", "Defense Evasion", "Adversaries may use NTFS attributes."),
    "T1564.005": ("Hidden File System", "Defense Evasion", "Adversaries may use hidden file systems."),
    "T1564.006": ("Run Virtual Instance", "Defense Evasion", "Adversaries may run virtual instances."),
    "T1564.007": ("VBA Stomping", "Defense Evasion", "Adversaries may use VBA stomping."),
    "T1564.008": ("Email Hiding Rules", "Defense Evasion", "Adversaries may use email hiding rules."),
    "T1564.009": ("Resource Forking", "Defense Evasion", "Adversaries may use resource forking."),
    "T1564.010": ("Process Argument Spoofing", "Defense Evasion", "Adversaries may spoof process arguments."),
    "T1564.011": ("Ignore Process Interrupts", "Defense Evasion", "Adversaries may ignore process interrupts."),
    "T1562": ("Impair Defenses", "Defense Evasion", "Adversaries may maliciously modify defenses to evade detection."),
    "T1562.001": ("Disable or Modify Tools", "Defense Evasion", "Adversaries may disable security tools."),
    "T1562.002": ("Disable Windows Event Logging", "Defense Evasion", "Adversaries may disable event logging."),
    "T1562.003": ("Impair Command History Logging", "Defense Evasion", "Adversaries may impair command history."),
    "T1562.004": ("Disable or Modify System Firewall", "Defense Evasion", "Adversaries may disable firewalls."),
    "T1562.006": ("Indicator Blocking", "Defense Evasion", "Adversaries may block indicators."),
    "T1562.007": ("Disable or Modify Cloud Firewall", "Defense Evasion", "Adversaries may disable cloud firewalls."),
    "T1562.008": ("Disable Cloud Logs", "Defense Evasion", "Adversaries may disable cloud logs."),
    "T1562.009": ("Safe Mode Boot", "Defense Evasion", "Adversaries may abuse safe mode boot."),
    "T1562.010": ("Downgrade Attack", "Defense Evasion", "Adversaries may downgrade security features."),
    "T1562.011": ("Spoof Security Alerting", "Defense Evasion", "Adversaries may spoof security alerts."),
    "T1562.012": ("Disable or Modify Linux Audit System", "Defense Evasion", "Adversaries may disable Linux audit."),
    "T1656": ("Impersonation", "Defense Evasion", "Adversaries may impersonate a trusted entity."),
    "T1070": ("Indicator Removal", "Defense Evasion", "Adversaries may delete or modify artifacts to hide activity."),
    "T1070.001": ("Clear Windows Event Logs", "Defense Evasion", "Adversaries may clear Windows event logs."),
    "T1070.002": ("Clear Linux or Mac System Logs", "Defense Evasion", "Adversaries may clear Unix logs."),
    "T1070.003": ("Clear Command History", "Defense Evasion", "Adversaries may clear command history."),
    "T1070.004": ("File Deletion", "Defense Evasion", "Adversaries may delete files."),
    "T1070.005": ("Network Share Connection Removal", "Defense Evasion", "Adversaries may remove share connections."),
    "T1070.006": ("Timestomp", "Defense Evasion", "Adversaries may modify timestamps."),
    "T1070.007": ("Clear Network Connection History and Configurations", "Defense Evasion", "Adversaries may clear network history."),
    "T1070.008": ("Clear Mailbox Data", "Defense Evasion", "Adversaries may clear mailbox data."),
    "T1070.009": ("Clear Persistence", "Defense Evasion", "Adversaries may clear persistence mechanisms."),
    "T1202": ("Indirect Command Execution", "Defense Evasion", "Adversaries may abuse utilities that execute commands indirectly."),
    "T1036": ("Masquerading", "Defense Evasion", "Adversaries may disguise malicious activity as legitimate."),
    "T1036.001": ("Invalid Code Signature", "Defense Evasion", "Adversaries may use invalid code signatures."),
    "T1036.002": ("Right-to-Left Override", "Defense Evasion", "Adversaries may use RTLO."),
    "T1036.003": ("Rename System Utilities", "Defense Evasion", "Adversaries may rename system utilities."),
    "T1036.004": ("Masquerade Task or Service", "Defense Evasion", "Adversaries may masquerade tasks/services."),
    "T1036.005": ("Match Legitimate Name or Location", "Defense Evasion", "Adversaries may match legitimate names."),
    "T1036.006": ("Space after Filename", "Defense Evasion", "Adversaries may use space after filename."),
    "T1036.007": ("Double File Extension", "Defense Evasion", "Adversaries may use double file extensions."),
    "T1036.008": ("Masquerade File Type", "Defense Evasion", "Adversaries may masquerade file types."),
    "T1036.009": ("Break Process Trees", "Defense Evasion", "Adversaries may break process trees."),
    "T1556": ("Modify Authentication Process", "Defense Evasion", "Adversaries may modify authentication."),
    "T1578": ("Modify Cloud Compute Infrastructure", "Defense Evasion", "Adversaries may modify cloud compute infrastructure to evade defenses."),
    "T1578.001": ("Create Snapshot", "Defense Evasion", "Adversaries may create cloud snapshots."),
    "T1578.002": ("Create Cloud Instance", "Defense Evasion", "Adversaries may create cloud instances."),
    "T1578.003": ("Delete Cloud Instance", "Defense Evasion", "Adversaries may delete cloud instances."),
    "T1578.004": ("Revert Cloud Instance", "Defense Evasion", "Adversaries may revert cloud instances."),
    "T1578.005": ("Modify Cloud Compute Configurations", "Defense Evasion", "Adversaries may modify cloud configs."),
    "T1112": ("Modify Registry", "Defense Evasion", "Adversaries may interact with the Windows Registry for persistence and evasion."),
    "T1601": ("Modify System Image", "Defense Evasion", "Adversaries may make changes to the operating system to weaken defenses."),
    "T1601.001": ("Patch System Image", "Defense Evasion", "Adversaries may patch system images."),
    "T1601.002": ("Downgrade System Image", "Defense Evasion", "Adversaries may downgrade system images."),
    "T1599": ("Network Boundary Bridging", "Defense Evasion", "Adversaries may bridge network boundaries to bypass restrictions."),
    "T1599.001": ("Network Address Translation Traversal", "Defense Evasion", "Adversaries may traverse NAT."),
    "T1027": ("Obfuscated Files or Information", "Defense Evasion", "Adversaries may encrypt, encode, or obfuscate content."),
    "T1027.001": ("Binary Padding", "Defense Evasion", "Adversaries may use binary padding."),
    "T1027.002": ("Software Packing", "Defense Evasion", "Adversaries may use software packing."),
    "T1027.003": ("Steganography", "Defense Evasion", "Adversaries may use steganography."),
    "T1027.004": ("Compile After Delivery", "Defense Evasion", "Adversaries may compile after delivery."),
    "T1027.005": ("Indicator Removal from Tools", "Defense Evasion", "Adversaries may remove indicators from tools."),
    "T1027.006": ("HTML Smuggling", "Defense Evasion", "Adversaries may use HTML smuggling."),
    "T1027.007": ("Dynamic API Resolution", "Defense Evasion", "Adversaries may use dynamic API resolution."),
    "T1027.008": ("Stripped Payloads", "Defense Evasion", "Adversaries may use stripped payloads."),
    "T1027.009": ("Embedded Payloads", "Defense Evasion", "Adversaries may use embedded payloads."),
    "T1027.010": ("Command Obfuscation", "Defense Evasion", "Adversaries may obfuscate commands."),
    "T1027.011": ("Fileless Storage", "Defense Evasion", "Adversaries may use fileless storage."),
    "T1027.012": ("LNK Icon Smuggling", "Defense Evasion", "Adversaries may use LNK icon smuggling."),
    "T1647": ("Plist File Modification", "Defense Evasion", "Adversaries may modify plist files to hide activity."),
    "T1620": ("Reflective Code Loading", "Defense Evasion", "Adversaries may reflectively load code into a process."),
    "T1207": ("Rogue Domain Controller", "Defense Evasion", "Adversaries may register a rogue Domain Controller to bypass controls."),
    "T1014": ("Rootkit", "Defense Evasion", "Adversaries may use rootkits to hide the presence of malware."),
    "T1553": ("Subvert Trust Controls", "Defense Evasion", "Adversaries may undermine security controls that will trust a component."),
    "T1553.001": ("Gatekeeper Bypass", "Defense Evasion", "Adversaries may bypass Gatekeeper."),
    "T1553.002": ("Code Signing", "Defense Evasion", "Adversaries may abuse code signing."),
    "T1553.003": ("SIP and Trust Provider Hijacking", "Defense Evasion", "Adversaries may hijack SIP/Trust providers."),
    "T1553.004": ("Install Root Certificate", "Defense Evasion", "Adversaries may install root certificates."),
    "T1553.005": ("Mark-of-the-Web Bypass", "Defense Evasion", "Adversaries may bypass MOTW."),
    "T1553.006": ("Code Signing Policy Modification", "Defense Evasion", "Adversaries may modify code signing policy."),
    "T1218": ("System Binary Proxy Execution", "Defense Evasion", "Adversaries may bypass defenses by proxying execution through trusted binaries."),
    "T1218.001": ("Compiled HTML File", "Defense Evasion", "Adversaries may use CHM files."),
    "T1218.002": ("Control Panel", "Defense Evasion", "Adversaries may abuse Control Panel."),
    "T1218.003": ("CMSTP", "Defense Evasion", "Adversaries may abuse CMSTP."),
    "T1218.004": ("InstallUtil", "Defense Evasion", "Adversaries may abuse InstallUtil."),
    "T1218.005": ("Mshta", "Defense Evasion", "Adversaries may abuse Mshta."),
    "T1218.007": ("Msiexec", "Defense Evasion", "Adversaries may abuse Msiexec."),
    "T1218.008": ("Odbcconf", "Defense Evasion", "Adversaries may abuse Odbcconf."),
    "T1218.009": ("Regsvcs/Regasm", "Defense Evasion", "Adversaries may abuse Regsvcs/Regasm."),
    "T1218.010": ("Regsvr32", "Defense Evasion", "Adversaries may abuse Regsvr32."),
    "T1218.011": ("Rundll32", "Defense Evasion", "Adversaries may abuse Rundll32."),
    "T1218.012": ("Verclsid", "Defense Evasion", "Adversaries may abuse Verclsid."),
    "T1218.013": ("Mavinject", "Defense Evasion", "Adversaries may abuse Mavinject."),
    "T1218.014": ("MMC", "Defense Evasion", "Adversaries may abuse MMC."),
    "T1216": ("System Script Proxy Execution", "Defense Evasion", "Adversaries may use scripts to proxy execution of malicious files."),
    "T1216.001": ("PubPrn", "Defense Evasion", "Adversaries may abuse PubPrn."),
    "T1216.002": ("SyncAppvPublishingServer", "Defense Evasion", "Adversaries may abuse SyncAppvPublishingServer."),
    "T1221": ("Template Injection", "Defense Evasion", "Adversaries may create or modify Office document templates."),
    "T1127": ("Trusted Developer Utilities Proxy Execution", "Defense Evasion", "Adversaries may take advantage of trusted developer utilities."),
    "T1127.001": ("MSBuild", "Defense Evasion", "Adversaries may abuse MSBuild."),
    "T1535": ("Unused/Unsupported Cloud Regions", "Defense Evasion", "Adversaries may create resources in unused geographic regions."),
    "T1550": ("Use Alternate Authentication Material", "Defense Evasion", "Adversaries may use alternate authentication material."),
    "T1550.001": ("Application Access Token", "Defense Evasion", "Adversaries may use app access tokens."),
    "T1550.002": ("Pass the Hash", "Defense Evasion", "Adversaries may use pass the hash."),
    "T1550.003": ("Pass the Ticket", "Defense Evasion", "Adversaries may use pass the ticket."),
    "T1550.004": ("Web Session Cookie", "Defense Evasion", "Adversaries may use web session cookies."),
    "T1497": ("Virtualization/Sandbox Evasion", "Defense Evasion", "Adversaries may detect virtualization and sandbox environments."),
    "T1497.001": ("System Checks", "Defense Evasion", "Adversaries may use system checks."),
    "T1497.002": ("User Activity Based Checks", "Defense Evasion", "Adversaries may check user activity."),
    "T1497.003": ("Time Based Evasion", "Defense Evasion", "Adversaries may use time-based evasion."),
    "T1600": ("Weaken Encryption", "Defense Evasion", "Adversaries may weaken encryption to aid in data compromise."),
    "T1600.001": ("Reduce Key Space", "Defense Evasion", "Adversaries may reduce key space."),
    "T1600.002": ("Disable Crypto Hardware", "Defense Evasion", "Adversaries may disable crypto hardware."),
    "T1220": ("XSL Script Processing", "Defense Evasion", "Adversaries may bypass security by using XSL script processing."),
    "T1642": ("Disable or Modify Cloud Firewall", "Defense Evasion", "Adversaries may disable or modify cloud firewall rules."),

    # ==================== CREDENTIAL ACCESS ====================
    "T1557": ("Adversary-in-the-Middle", "Credential Access", "Adversaries may attempt to position themselves between two entities."),
    "T1557.001": ("LLMNR/NBT-NS Poisoning and SMB Relay", "Credential Access", "Adversaries may poison LLMNR/NBT-NS."),
    "T1557.002": ("ARP Cache Poisoning", "Credential Access", "Adversaries may poison ARP cache."),
    "T1557.003": ("DHCP Spoofing", "Credential Access", "Adversaries may spoof DHCP."),
    "T1110": ("Brute Force", "Credential Access", "Adversaries may use brute force techniques to gain access to accounts."),
    "T1110.001": ("Password Guessing", "Credential Access", "Adversaries may guess passwords."),
    "T1110.002": ("Password Cracking", "Credential Access", "Adversaries may crack passwords."),
    "T1110.003": ("Password Spraying", "Credential Access", "Adversaries may spray passwords."),
    "T1110.004": ("Credential Stuffing", "Credential Access", "Adversaries may stuff credentials."),
    "T1555": ("Credentials from Password Stores", "Credential Access", "Adversaries may search for common password storage locations."),
    "T1555.001": ("Keychain", "Credential Access", "Adversaries may access Keychain."),
    "T1555.002": ("Securityd Memory", "Credential Access", "Adversaries may access securityd memory."),
    "T1555.003": ("Credentials from Web Browsers", "Credential Access", "Adversaries may get browser credentials."),
    "T1555.004": ("Windows Credential Manager", "Credential Access", "Adversaries may access Windows Credential Manager."),
    "T1555.005": ("Password Managers", "Credential Access", "Adversaries may target password managers."),
    "T1555.006": ("Cloud Secrets Management Stores", "Credential Access", "Adversaries may access cloud secrets."),
    "T1212": ("Exploitation for Credential Access", "Credential Access", "Adversaries may exploit software vulnerabilities to collect credentials."),
    "T1187": ("Forced Authentication", "Credential Access", "Adversaries may gather credential material by forcing authentication."),
    "T1606": ("Forge Web Credentials", "Credential Access", "Adversaries may forge credential materials that can be used to access web apps."),
    "T1606.001": ("Web Cookies", "Credential Access", "Adversaries may forge web cookies."),
    "T1606.002": ("SAML Tokens", "Credential Access", "Adversaries may forge SAML tokens."),
    "T1056": ("Input Capture", "Credential Access", "Adversaries may use methods of capturing user input to obtain credentials."),
    "T1056.001": ("Keylogging", "Credential Access", "Adversaries may use keyloggers."),
    "T1056.002": ("GUI Input Capture", "Credential Access", "Adversaries may capture GUI input."),
    "T1056.003": ("Web Portal Capture", "Credential Access", "Adversaries may capture web portal input."),
    "T1056.004": ("Credential API Hooking", "Credential Access", "Adversaries may hook credential APIs."),
    "T1040": ("Network Sniffing", "Credential Access", "Adversaries may sniff network traffic to capture credentials."),
    "T1003": ("OS Credential Dumping", "Credential Access", "Adversaries may attempt to dump credentials from the operating system."),
    "T1003.001": ("LSASS Memory", "Credential Access", "Adversaries may dump LSASS memory."),
    "T1003.002": ("Security Account Manager", "Credential Access", "Adversaries may dump SAM."),
    "T1003.003": ("NTDS", "Credential Access", "Adversaries may dump NTDS."),
    "T1003.004": ("LSA Secrets", "Credential Access", "Adversaries may dump LSA secrets."),
    "T1003.005": ("Cached Domain Credentials", "Credential Access", "Adversaries may dump cached credentials."),
    "T1003.006": ("DCSync", "Credential Access", "Adversaries may use DCSync."),
    "T1003.007": ("Proc Filesystem", "Credential Access", "Adversaries may dump /proc filesystem."),
    "T1003.008": ("/etc/passwd and /etc/shadow", "Credential Access", "Adversaries may dump /etc/passwd and shadow."),
    "T1528": ("Steal Application Access Token", "Credential Access", "Adversaries may steal application access tokens."),
    "T1649": ("Steal or Forge Authentication Certificates", "Credential Access", "Adversaries may steal or forge certificates."),
    "T1558": ("Steal or Forge Kerberos Tickets", "Credential Access", "Adversaries may steal or forge Kerberos tickets."),
    "T1558.001": ("Golden Ticket", "Credential Access", "Adversaries may create Golden Tickets."),
    "T1558.002": ("Silver Ticket", "Credential Access", "Adversaries may create Silver Tickets."),
    "T1558.003": ("Kerberoasting", "Credential Access", "Adversaries may use Kerberoasting."),
    "T1558.004": ("AS-REP Roasting", "Credential Access", "Adversaries may use AS-REP Roasting."),
    "T1539": ("Steal Web Session Cookie", "Credential Access", "Adversaries may steal web session cookies."),
    "T1111": ("Multi-Factor Authentication Interception", "Credential Access", "Adversaries may target MFA mechanisms."),
    "T1621": ("Multi-Factor Authentication Request Generation", "Credential Access", "Adversaries may attempt to bypass MFA by generating requests."),
    "T1552": ("Unsecured Credentials", "Credential Access", "Adversaries may search for unsecured credentials in files."),
    "T1552.001": ("Credentials In Files", "Credential Access", "Adversaries may search files for credentials."),
    "T1552.002": ("Credentials in Registry", "Credential Access", "Adversaries may search registry for credentials."),
    "T1552.003": ("Bash History", "Credential Access", "Adversaries may search bash history."),
    "T1552.004": ("Private Keys", "Credential Access", "Adversaries may search for private keys."),
    "T1552.005": ("Cloud Instance Metadata API", "Credential Access", "Adversaries may access cloud metadata API."),
    "T1552.006": ("Group Policy Preferences", "Credential Access", "Adversaries may search GPP."),
    "T1552.007": ("Container API", "Credential Access", "Adversaries may access container APIs."),
    "T1552.008": ("Chat Messages", "Credential Access", "Adversaries may search chat messages."),

    # ==================== DISCOVERY ====================
    "T1087": ("Account Discovery", "Discovery", "Adversaries may attempt to get a listing of accounts on a system."),
    "T1087.001": ("Local Account", "Discovery", "Adversaries may enumerate local accounts."),
    "T1087.002": ("Domain Account", "Discovery", "Adversaries may enumerate domain accounts."),
    "T1087.003": ("Email Account", "Discovery", "Adversaries may enumerate email accounts."),
    "T1087.004": ("Cloud Account", "Discovery", "Adversaries may enumerate cloud accounts."),
    "T1010": ("Application Window Discovery", "Discovery", "Adversaries may attempt to get a listing of open application windows."),
    "T1217": ("Browser Information Discovery", "Discovery", "Adversaries may enumerate browser information."),
    "T1580": ("Cloud Infrastructure Discovery", "Discovery", "Adversaries may enumerate cloud infrastructure."),
    "T1538": ("Cloud Service Dashboard", "Discovery", "Adversaries may use cloud service dashboards for discovery."),
    "T1526": ("Cloud Service Discovery", "Discovery", "Adversaries may enumerate cloud services."),
    "T1613": ("Container and Resource Discovery", "Discovery", "Adversaries may attempt to discover containers and resources."),
    "T1652": ("Device Driver Discovery", "Discovery", "Adversaries may enumerate device drivers."),
    "T1482": ("Domain Trust Discovery", "Discovery", "Adversaries may gather information about domain trust relationships."),
    "T1083": ("File and Directory Discovery", "Discovery", "Adversaries may enumerate files and directories."),
    "T1615": ("Group Policy Discovery", "Discovery", "Adversaries may gather information on Group Policy settings."),
    "T1654": ("Log Enumeration", "Discovery", "Adversaries may enumerate system and service logs."),
    "T1046": ("Network Service Discovery", "Discovery", "Adversaries may scan for services running on remote hosts."),
    "T1135": ("Network Share Discovery", "Discovery", "Adversaries may look for shared folders and drives on remote systems."),
    "T1201": ("Password Policy Discovery", "Discovery", "Adversaries may attempt to discover password policy information."),
    "T1120": ("Peripheral Device Discovery", "Discovery", "Adversaries may attempt to discover peripheral devices."),
    "T1069": ("Permission Groups Discovery", "Discovery", "Adversaries may discover permission groups."),
    "T1069.001": ("Local Groups", "Discovery", "Adversaries may enumerate local groups."),
    "T1069.002": ("Domain Groups", "Discovery", "Adversaries may enumerate domain groups."),
    "T1069.003": ("Cloud Groups", "Discovery", "Adversaries may enumerate cloud groups."),
    "T1057": ("Process Discovery", "Discovery", "Adversaries may enumerate running processes."),
    "T1012": ("Query Registry", "Discovery", "Adversaries may query the Registry to find information."),
    "T1018": ("Remote System Discovery", "Discovery", "Adversaries may scan for remote systems."),
    "T1518": ("Software Discovery", "Discovery", "Adversaries may discover installed software."),
    "T1518.001": ("Security Software Discovery", "Discovery", "Adversaries may discover security software."),
    "T1082": ("System Information Discovery", "Discovery", "Adversaries may collect detailed system information."),
    "T1614": ("System Location Discovery", "Discovery", "Adversaries may discover system location information."),
    "T1614.001": ("System Language Discovery", "Discovery", "Adversaries may discover system language."),
    "T1016": ("System Network Configuration Discovery", "Discovery", "Adversaries may look for network configuration."),
    "T1016.001": ("Internet Connection Discovery", "Discovery", "Adversaries may check internet connectivity."),
    "T1049": ("System Network Connections Discovery", "Discovery", "Adversaries may enumerate network connections."),
    "T1033": ("System Owner/User Discovery", "Discovery", "Adversaries may identify the primary user of a system."),
    "T1007": ("System Service Discovery", "Discovery", "Adversaries may enumerate services running on a system."),
    "T1124": ("System Time Discovery", "Discovery", "Adversaries may gather the system time and/or time zone."),
    "T1497": ("Virtualization/Sandbox Evasion", "Discovery", "Adversaries may detect virtualization/sandbox."),

    # ==================== LATERAL MOVEMENT ====================
    "T1210": ("Exploitation of Remote Services", "Lateral Movement", "Adversaries may exploit remote services to move laterally."),
    "T1534": ("Internal Spearphishing", "Lateral Movement", "Adversaries may use internal spearphishing."),
    "T1570": ("Lateral Tool Transfer", "Lateral Movement", "Adversaries may transfer tools between systems."),
    "T1563": ("Remote Service Session Hijacking", "Lateral Movement", "Adversaries may hijack existing remote sessions."),
    "T1563.001": ("SSH Hijacking", "Lateral Movement", "Adversaries may hijack SSH sessions."),
    "T1563.002": ("RDP Hijacking", "Lateral Movement", "Adversaries may hijack RDP sessions."),
    "T1021": ("Remote Services", "Lateral Movement", "Adversaries may use valid accounts to log into remote services."),
    "T1021.001": ("Remote Desktop Protocol", "Lateral Movement", "Adversaries may use RDP."),
    "T1021.002": ("SMB/Windows Admin Shares", "Lateral Movement", "Adversaries may use SMB/admin shares."),
    "T1021.003": ("Distributed Component Object Model", "Lateral Movement", "Adversaries may use DCOM."),
    "T1021.004": ("SSH", "Lateral Movement", "Adversaries may use SSH."),
    "T1021.005": ("VNC", "Lateral Movement", "Adversaries may use VNC."),
    "T1021.006": ("Windows Remote Management", "Lateral Movement", "Adversaries may use WinRM."),
    "T1021.007": ("Cloud Services", "Lateral Movement", "Adversaries may use cloud services."),
    "T1021.008": ("Direct Cloud VM Connections", "Lateral Movement", "Adversaries may use direct cloud VM connections."),
    "T1091": ("Replication Through Removable Media", "Lateral Movement", "Adversaries may use removable media."),
    "T1072": ("Software Deployment Tools", "Lateral Movement", "Adversaries may use deployment tools."),
    "T1080": ("Taint Shared Content", "Lateral Movement", "Adversaries may deliver payloads via shared content."),
    "T1550": ("Use Alternate Authentication Material", "Lateral Movement", "Adversaries may use alternate auth material."),

    # ==================== COLLECTION ====================
    "T1557": ("Adversary-in-the-Middle", "Collection", "Adversaries may position themselves between entities."),
    "T1560": ("Archive Collected Data", "Collection", "Adversaries may archive collected data prior to exfiltration."),
    "T1560.001": ("Archive via Utility", "Collection", "Adversaries may archive using utilities."),
    "T1560.002": ("Archive via Library", "Collection", "Adversaries may archive using libraries."),
    "T1560.003": ("Archive via Custom Method", "Collection", "Adversaries may archive using custom methods."),
    "T1123": ("Audio Capture", "Collection", "Adversaries may attempt to capture audio."),
    "T1119": ("Automated Collection", "Collection", "Adversaries may use automated techniques to collect data."),
    "T1185": ("Browser Session Hijacking", "Collection", "Adversaries may exploit browser session hijacking."),
    "T1115": ("Clipboard Data", "Collection", "Adversaries may collect data stored in the clipboard."),
    "T1530": ("Data from Cloud Storage", "Collection", "Adversaries may access data from cloud storage."),
    "T1602": ("Data from Configuration Repository", "Collection", "Adversaries may collect data from configuration repositories."),
    "T1602.001": ("SNMP (MIB Dump)", "Collection", "Adversaries may dump SNMP MIBs."),
    "T1602.002": ("Network Device Configuration Dump", "Collection", "Adversaries may dump network device configs."),
    "T1213": ("Data from Information Repositories", "Collection", "Adversaries may leverage information repositories."),
    "T1213.001": ("Confluence", "Collection", "Adversaries may access Confluence."),
    "T1213.002": ("Sharepoint", "Collection", "Adversaries may access Sharepoint."),
    "T1213.003": ("Code Repositories", "Collection", "Adversaries may access code repositories."),
    "T1005": ("Data from Local System", "Collection", "Adversaries may search local system sources for data."),
    "T1039": ("Data from Network Shared Drive", "Collection", "Adversaries may search network shares for files of interest."),
    "T1025": ("Data from Removable Media", "Collection", "Adversaries may search connected removable media."),
    "T1074": ("Data Staged", "Collection", "Adversaries may stage collected data in a central location."),
    "T1074.001": ("Local Data Staging", "Collection", "Adversaries may stage data locally."),
    "T1074.002": ("Remote Data Staging", "Collection", "Adversaries may stage data remotely."),
    "T1114": ("Email Collection", "Collection", "Adversaries may target user email to collect sensitive information."),
    "T1114.001": ("Local Email Collection", "Collection", "Adversaries may collect local email."),
    "T1114.002": ("Remote Email Collection", "Collection", "Adversaries may collect remote email."),
    "T1114.003": ("Email Forwarding Rule", "Collection", "Adversaries may use email forwarding rules."),
    "T1056": ("Input Capture", "Collection", "Adversaries may capture user input."),
    "T1113": ("Screen Capture", "Collection", "Adversaries may attempt to capture screenshots."),
    "T1125": ("Video Capture", "Collection", "Adversaries may attempt to capture video."),

    # ==================== COMMAND AND CONTROL ====================
    "T1071": ("Application Layer Protocol", "Command and Control", "Adversaries may communicate using OSI application layer protocols."),
    "T1071.001": ("Web Protocols", "Command and Control", "Adversaries may use web protocols."),
    "T1071.002": ("File Transfer Protocols", "Command and Control", "Adversaries may use file transfer protocols."),
    "T1071.003": ("Mail Protocols", "Command and Control", "Adversaries may use mail protocols."),
    "T1071.004": ("DNS", "Command and Control", "Adversaries may use DNS."),
    "T1092": ("Communication Through Removable Media", "Command and Control", "Adversaries may perform command and control through removable media."),
    "T1659": ("Content Injection", "Command and Control", "Adversaries may inject content for C2."),
    "T1132": ("Data Encoding", "Command and Control", "Adversaries may encode data to make communication less conspicuous."),
    "T1132.001": ("Standard Encoding", "Command and Control", "Adversaries may use standard encoding."),
    "T1132.002": ("Non-Standard Encoding", "Command and Control", "Adversaries may use non-standard encoding."),
    "T1001": ("Data Obfuscation", "Command and Control", "Adversaries may obfuscate command and control traffic."),
    "T1001.001": ("Junk Data", "Command and Control", "Adversaries may add junk data."),
    "T1001.002": ("Steganography", "Command and Control", "Adversaries may use steganography."),
    "T1001.003": ("Protocol Impersonation", "Command and Control", "Adversaries may impersonate protocols."),
    "T1568": ("Dynamic Resolution", "Command and Control", "Adversaries may dynamically resolve C2 addresses."),
    "T1568.001": ("Fast Flux DNS", "Command and Control", "Adversaries may use fast flux DNS."),
    "T1568.002": ("Domain Generation Algorithms", "Command and Control", "Adversaries may use DGAs."),
    "T1568.003": ("DNS Calculation", "Command and Control", "Adversaries may calculate DNS addresses."),
    "T1573": ("Encrypted Channel", "Command and Control", "Adversaries may employ encryption to conceal C2 traffic."),
    "T1573.001": ("Symmetric Cryptography", "Command and Control", "Adversaries may use symmetric crypto."),
    "T1573.002": ("Asymmetric Cryptography", "Command and Control", "Adversaries may use asymmetric crypto."),
    "T1008": ("Fallback Channels", "Command and Control", "Adversaries may use fallback communication channels."),
    "T1105": ("Ingress Tool Transfer", "Command and Control", "Adversaries may transfer tools from external systems."),
    "T1104": ("Multi-Stage Channels", "Command and Control", "Adversaries may create multiple stages for C2."),
    "T1095": ("Non-Application Layer Protocol", "Command and Control", "Adversaries may use non-application layer protocols for C2."),
    "T1571": ("Non-Standard Port", "Command and Control", "Adversaries may use non-standard ports for C2."),
    "T1572": ("Protocol Tunneling", "Command and Control", "Adversaries may tunnel network communications to evade detection."),
    "T1090": ("Proxy", "Command and Control", "Adversaries may use a proxy to direct network traffic."),
    "T1090.001": ("Internal Proxy", "Command and Control", "Adversaries may use internal proxies."),
    "T1090.002": ("External Proxy", "Command and Control", "Adversaries may use external proxies."),
    "T1090.003": ("Multi-hop Proxy", "Command and Control", "Adversaries may use multi-hop proxies."),
    "T1090.004": ("Domain Fronting", "Command and Control", "Adversaries may use domain fronting."),
    "T1219": ("Remote Access Software", "Command and Control", "Adversaries may use legitimate desktop support software."),
    "T1205": ("Traffic Signaling", "Command and Control", "Adversaries may use traffic signaling."),
    "T1102": ("Web Service", "Command and Control", "Adversaries may use legitimate web services for C2."),
    "T1102.001": ("Dead Drop Resolver", "Command and Control", "Adversaries may use dead drop resolvers."),
    "T1102.002": ("Bidirectional Communication", "Command and Control", "Adversaries may use bidirectional web services."),
    "T1102.003": ("One-Way Communication", "Command and Control", "Adversaries may use one-way web services."),

    # ==================== EXFILTRATION ====================
    "T1020": ("Automated Exfiltration", "Exfiltration", "Adversaries may exfiltrate data using automated processing."),
    "T1020.001": ("Traffic Duplication", "Exfiltration", "Adversaries may duplicate traffic."),
    "T1030": ("Data Transfer Size Limits", "Exfiltration", "Adversaries may exfiltrate data in fixed size chunks."),
    "T1048": ("Exfiltration Over Alternative Protocol", "Exfiltration", "Adversaries may steal data by exfiltrating over different protocols."),
    "T1048.001": ("Exfiltration Over Symmetric Encrypted Non-C2 Protocol", "Exfiltration", "Exfil over symmetric encrypted protocol."),
    "T1048.002": ("Exfiltration Over Asymmetric Encrypted Non-C2 Protocol", "Exfiltration", "Exfil over asymmetric encrypted protocol."),
    "T1048.003": ("Exfiltration Over Unencrypted Non-C2 Protocol", "Exfiltration", "Exfil over unencrypted protocol."),
    "T1041": ("Exfiltration Over C2 Channel", "Exfiltration", "Adversaries may steal data by exfiltrating over existing C2."),
    "T1011": ("Exfiltration Over Other Network Medium", "Exfiltration", "Adversaries may exfiltrate via different network medium."),
    "T1011.001": ("Exfiltration Over Bluetooth", "Exfiltration", "Adversaries may exfil over Bluetooth."),
    "T1052": ("Exfiltration Over Physical Medium", "Exfiltration", "Adversaries may attempt to exfiltrate via physical medium."),
    "T1052.001": ("Exfiltration over USB", "Exfiltration", "Adversaries may exfil over USB."),
    "T1567": ("Exfiltration Over Web Service", "Exfiltration", "Adversaries may use web service to exfiltrate data."),
    "T1567.001": ("Exfiltration to Code Repository", "Exfiltration", "Adversaries may exfil to code repos."),
    "T1567.002": ("Exfiltration to Cloud Storage", "Exfiltration", "Adversaries may exfil to cloud storage."),
    "T1567.003": ("Exfiltration to Text Storage Sites", "Exfiltration", "Adversaries may exfil to text storage sites."),
    "T1567.004": ("Exfiltration Over Webhook", "Exfiltration", "Adversaries may exfil over webhooks."),
    "T1029": ("Scheduled Transfer", "Exfiltration", "Adversaries may schedule data exfiltration at certain times."),
    "T1537": ("Transfer Data to Cloud Account", "Exfiltration", "Adversaries may exfiltrate data to a cloud account."),

    # ==================== IMPACT ====================
    "T1531": ("Account Access Removal", "Impact", "Adversaries may interrupt availability by inhibiting access to accounts."),
    "T1485": ("Data Destruction", "Impact", "Adversaries may destroy data and files on specific systems."),
    "T1486": ("Data Encrypted for Impact", "Impact", "Adversaries may encrypt data to interrupt availability."),
    "T1565": ("Data Manipulation", "Impact", "Adversaries may manipulate data to affect process integrity."),
    "T1565.001": ("Stored Data Manipulation", "Impact", "Adversaries may manipulate stored data."),
    "T1565.002": ("Transmitted Data Manipulation", "Impact", "Adversaries may manipulate transmitted data."),
    "T1565.003": ("Runtime Data Manipulation", "Impact", "Adversaries may manipulate runtime data."),
    "T1491": ("Defacement", "Impact", "Adversaries may modify visual content for messaging or intimidation."),
    "T1491.001": ("Internal Defacement", "Impact", "Adversaries may deface internal resources."),
    "T1491.002": ("External Defacement", "Impact", "Adversaries may deface external resources."),
    "T1561": ("Disk Wipe", "Impact", "Adversaries may wipe or corrupt raw disk data."),
    "T1561.001": ("Disk Content Wipe", "Impact", "Adversaries may wipe disk content."),
    "T1561.002": ("Disk Structure Wipe", "Impact", "Adversaries may wipe disk structure."),
    "T1499": ("Endpoint Denial of Service", "Impact", "Adversaries may perform DoS attacks targeting endpoint systems."),
    "T1499.001": ("OS Exhaustion Flood", "Impact", "Adversaries may exhaust OS resources."),
    "T1499.002": ("Service Exhaustion Flood", "Impact", "Adversaries may exhaust service resources."),
    "T1499.003": ("Application Exhaustion Flood", "Impact", "Adversaries may exhaust application resources."),
    "T1499.004": ("Application or System Exploitation", "Impact", "Adversaries may exploit apps/systems for DoS."),
    "T1657": ("Financial Theft", "Impact", "Adversaries may steal monetary resources."),
    "T1495": ("Firmware Corruption", "Impact", "Adversaries may overwrite or corrupt firmware."),
    "T1490": ("Inhibit System Recovery", "Impact", "Adversaries may delete or remove data to inhibit recovery."),
    "T1498": ("Network Denial of Service", "Impact", "Adversaries may perform DoS attacks to degrade network availability."),
    "T1498.001": ("Direct Network Flood", "Impact", "Adversaries may directly flood networks."),
    "T1498.002": ("Reflection Amplification", "Impact", "Adversaries may use reflection amplification."),
    "T1496": ("Resource Hijacking", "Impact", "Adversaries may leverage resources for resource-intensive tasks."),
    "T1489": ("Service Stop", "Impact", "Adversaries may stop or disable services on a system."),
    "T1529": ("System Shutdown/Reboot", "Impact", "Adversaries may shutdown/reboot systems to interrupt access."),
}


def generate_technique_xml(technique_id, name, tactic, description):
    """Generate XML dashboard for a specific technique."""
    tid_lower = technique_id.lower().replace(".", "_")

    return f'''<form version="1.1" stylesheet="mitre.css" theme="dark">
  <label>{technique_id} - {name}</label>
  <description>{description}</description>
  <search id="base">
    <query>index=* host=* | dedup index host | table index host</query>
    <earliest>$time_tok.earliest$</earliest>
    <latest>$time_tok.latest$</latest>
  </search>
  <search id="technique_base">
    <query>index=$case_tok$ host=$host_tok$ mitre_id="{technique_id}*"</query>
    <earliest>$time_tok.earliest$</earliest>
    <latest>$time_tok.latest$</latest>
  </search>
  <fieldset submitButton="true" autoRun="true">
    <input type="dropdown" token="case_tok" searchWhenChanged="false">
      <label>Select a Case:</label>
      <choice value="*">All</choice>
      <default>*</default>
      <initialValue>*</initialValue>
      <fieldForLabel>index</fieldForLabel>
      <fieldForValue>index</fieldForValue>
      <search base="base">
        <query>| search host=$host_tok$ | dedup index | sort index</query>
      </search>
      <prefix>"</prefix>
      <suffix>"</suffix>
    </input>
    <input type="dropdown" token="host_tok" searchWhenChanged="false">
      <label>Select a Host:</label>
      <choice value="*">All</choice>
      <default>*</default>
      <initialValue>*</initialValue>
      <fieldForLabel>host</fieldForLabel>
      <fieldForValue>host</fieldForValue>
      <search base="base">
        <query>| search index=$case_tok$ | dedup host | sort host</query>
      </search>
      <prefix>"</prefix>
      <suffix>"</suffix>
    </input>
    <input type="time" token="time_tok" searchWhenChanged="false">
      <label>Select a Time Range:</label>
      <default>
        <earliest>0</earliest>
        <latest></latest>
      </default>
    </input>
  </fieldset>
  <row>
    <panel>
      <title>Technique Overview</title>
      <html>
        <style>
          .technique-info {{ padding: 15px; background: #1a1a1a; border-radius: 8px; }}
          .technique-info h3 {{ color: #00bcd4; margin-bottom: 10px; }}
          .technique-info p {{ color: #b0b0b0; line-height: 1.6; }}
          .tactic-badge {{ display: inline-block; background: #26a69a; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; }}
        </style>
        <div class="technique-info">
          <span class="tactic-badge">{tactic}</span>
          <h3>{technique_id} - {name}</h3>
          <p>{description}</p>
        </div>
      </html>
    </panel>
  </row>
  <row>
    <panel>
      <title>Sub-techniques Count</title>
      <single>
        <search>
          <query>| inputlookup mitre.csv | search id="{technique_id}*" | stats count</query>
        </search>
        <option name="colorBy">value</option>
        <option name="colorMode">block</option>
        <option name="drilldown">none</option>
        <option name="height">80</option>
        <option name="rangeColors">["0x53a051","0x0877a6","0xf8be34","0xf1813f","0xdc4e41"]</option>
        <option name="useColors">1</option>
        <option name="unit">techniques</option>
      </single>
    </panel>
    <panel>
      <title>Events Detected</title>
      <single>
        <search base="technique_base">
          <query>| stats count</query>
        </search>
        <option name="colorBy">value</option>
        <option name="colorMode">block</option>
        <option name="drilldown">none</option>
        <option name="height">80</option>
        <option name="rangeColors">["0x555555","0x6db7c6","0x65a637"]</option>
        <option name="rangeValues">[0,1]</option>
        <option name="useColors">1</option>
      </single>
    </panel>
    <panel>
      <title>Unique Hosts</title>
      <single>
        <search base="technique_base">
          <query>| stats dc(host) AS hosts</query>
        </search>
        <option name="colorBy">value</option>
        <option name="colorMode">block</option>
        <option name="drilldown">none</option>
        <option name="height">80</option>
        <option name="rangeColors">["0x555555","0xf8be34","0xdc4e41"]</option>
        <option name="rangeValues">[0,1]</option>
        <option name="useColors">1</option>
        <option name="unit">hosts</option>
      </single>
    </panel>
  </row>
  <row>
    <panel>
      <title>Events Timeline</title>
      <chart>
        <search base="technique_base">
          <query>| timechart count BY mitre_technique</query>
        </search>
        <option name="charting.chart">area</option>
        <option name="charting.chart.stackMode">stacked</option>
        <option name="charting.drilldown">none</option>
        <option name="charting.legend.placement">bottom</option>
        <option name="charting.chart.nullValueMode">zero</option>
        <option name="height">250</option>
        <option name="refresh.display">progressbar</option>
      </chart>
    </panel>
  </row>
  <row>
    <panel>
      <title>Sub-Techniques Distribution</title>
      <chart>
        <search base="technique_base">
          <query>| stats count BY mitre_id | sort -count | head 20</query>
        </search>
        <option name="charting.chart">pie</option>
        <option name="charting.drilldown">none</option>
        <option name="height">300</option>
        <option name="refresh.display">progressbar</option>
      </chart>
    </panel>
    <panel>
      <title>Affected Hosts</title>
      <chart>
        <search base="technique_base">
          <query>| stats count BY host | sort -count | head 20</query>
        </search>
        <option name="charting.chart">bar</option>
        <option name="charting.drilldown">none</option>
        <option name="height">300</option>
        <option name="refresh.display">progressbar</option>
      </chart>
    </panel>
  </row>
  <row>
    <panel>
      <title>Event Details</title>
      <table>
        <search base="technique_base">
          <query>| `convert_time` | table Time index host mitre_id mitre_technique logtype source | sort -Time | rename Time AS "Time" index AS "Case" host AS "Host" mitre_id AS "Technique ID" mitre_technique AS "Technique" logtype AS "Log Type" source AS "Source"</query>
        </search>
        <option name="count">20</option>
        <option name="drilldown">cell</option>
        <option name="refresh.display">progressbar</option>
        <option name="wrap">false</option>
        <drilldown>
          <link target="_blank">/app/elrond/search?q=search%20index%3D$row.Case$%20host%3D$row.Host$%20mitre_id%3D"$row.Technique ID$"</link>
        </drilldown>
      </table>
    </panel>
  </row>
  <row>
    <panel>
      <title>MITRE ATT&amp;CK Reference</title>
      <table>
        <search>
          <query>| inputlookup mitre.csv | search id="{technique_id}*" | table id name tactic platform procedure_example detection | rename id AS "ID" name AS "Name" tactic AS "Tactic" platform AS "Platform" procedure_example AS "Threat Groups" detection AS "Detection"</query>
        </search>
        <option name="count">10</option>
        <option name="drilldown">none</option>
        <option name="refresh.display">progressbar</option>
        <option name="wrap">true</option>
      </table>
    </panel>
  </row>
</form>'''


def create_all_technique_xmls(views_dir):
    """Generate all technique XML files in the specified directory."""
    import os
    count = 0
    for tid, (name, tactic, description) in TECHNIQUES.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        # Replace dots with underscores for sub-technique filenames
        filename = os.path.join(views_dir, f"{tid.lower().replace('.', '_')}.xml")
        with open(filename, 'w') as f:
            f.write(xml_content)
        count += 1
    return count


# Tactic-based generation functions for backwards compatibility
def create_initial_access_xml(sd):
    """Generate Initial Access technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Initial Access"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_execution_xml(sd):
    """Generate Execution technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Execution"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_persistence_xml(sd):
    """Generate Persistence technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Persistence"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_privilege_escalation_xml(sd):
    """Generate Privilege Escalation technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Privilege Escalation"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_defense_evasion_xml(sd):
    """Generate Defense Evasion technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Defense Evasion"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_credential_access_xml(sd):
    """Generate Credential Access technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Credential Access"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_discovery_xml(sd):
    """Generate Discovery technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Discovery"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_lateral_movement_xml(sd):
    """Generate Lateral Movement technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Lateral Movement"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_collection_xml(sd):
    """Generate Collection technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Collection"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_command_and_control_xml(sd):
    """Generate Command and Control technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Command and Control"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_exfiltration_xml(sd):
    """Generate Exfiltration technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Exfiltration"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_impact_xml(sd):
    """Generate Impact technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Impact"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_reconnaissance_xml(sd):
    """Generate Reconnaissance technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Reconnaissance"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


def create_resource_development_xml(sd):
    """Generate Resource Development technique XMLs."""
    techniques = {k: v for k, v in TECHNIQUES.items() if v[1] == "Resource Development"}
    for tid, (name, tactic, description) in techniques.items():
        xml_content = generate_technique_xml(tid, name, tactic, description)
        with open(f"{sd}{tid.lower().replace('.', '_')}.xml", 'w') as f:
            f.write(xml_content)


if __name__ == "__main__":
    # Test generation
    import sys
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = "."

    count = create_all_technique_xmls(output_dir)
    print(f"Generated {count} technique dashboards")

    # Print technique counts by tactic
    tactics = {}
    for tid, (name, tactic, desc) in TECHNIQUES.items():
        tactics[tactic] = tactics.get(tactic, 0) + 1

    print("\nTechniques by tactic:")
    for tactic, count in sorted(tactics.items()):
        print(f"  {tactic}: {count}")
