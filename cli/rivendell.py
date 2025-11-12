#!/usr/bin/env python3
"""
Rivendell - Unified Digital Forensics Suite
Combining Gandalf (acquisition) and Elrond (analysis)

Usage:
    rivendell acquire [options]   - Acquire forensic artifacts (Gandalf)
    rivendell analyze [options]   - Analyze forensic artifacts (Elrond)
    rivendell web [options]        - Start web interface
    rivendell --version            - Show version
    rivendell --help               - Show help
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
RIVENDELL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(RIVENDELL_ROOT / "analysis"))
sys.path.insert(0, str(RIVENDELL_ROOT / "acquisition" / "python"))

VERSION = "2.0.0"

def print_banner():
    """Print Rivendell banner"""
    banner = r"""
    ____  _                     __     ____
   |  _ \(_)_   _____ _ __   __| | ___| | |
   | |_) | \ \ / / _ \ '_ \ / _` |/ _ \ | |
   |  _ <| |\ V /  __/ | | | (_| |  __/ | |
   |_| \_\_| \_/ \___|_| |_|\__,_|\___|_|_|

   Digital Forensics Suite - Acquisition & Analysis
   Version {}

   Gandalf: Remote Forensic Acquisition
   Elrond:  Automated Forensic Analysis
""".format(VERSION)
    print(banner)


def cmd_acquire(args):
    """Run Gandalf acquisition"""
    print("[*] Starting Gandalf acquisition module...")

    # Import gandalf
    try:
        import gandalf
        # Pass through to gandalf's main
        gandalf_args = [args.encryption, args.mode]
        if args.output:
            gandalf_args.extend(['-O', args.output])
        if args.memory:
            gandalf_args.append('-M')
        if args.access_times:
            gandalf_args.append('-A')
        if args.collect_files:
            gandalf_args.append('-C')

        # TODO: Call gandalf main with args
        print(f"[*] Would execute: gandalf {' '.join(gandalf_args)}")
        print("[!] Direct integration pending - use acquisition/python/gandalf.py for now")

    except ImportError:
        print("[ERROR] Gandalf module not found")
        print("[*] Use: python3 acquisition/python/gandalf.py")
        return 1

    return 0


def cmd_analyze(args):
    """Run Elrond analysis"""
    print("[*] Starting Elrond analysis module...")

    # Import elrond
    try:
        from analysis import elrond
        # Pass through to elrond's main
        elrond_args = [args.case_id, args.evidence_path]
        if args.output:
            elrond_args.append(args.output)

        # Build flag string
        flags = []
        if args.collect:
            flags.append('-C')
        if args.process:
            flags.append('-P')
        if args.analyze:
            flags.append('-A')
        if args.splunk:
            flags.append('-S')
        if args.elastic:
            flags.append('-E')
        if args.brisk:
            flags.append('-B')

        if flags:
            elrond_args.append(''.join(flags))

        # TODO: Call elrond main with args
        print(f"[*] Would execute: elrond {' '.join(elrond_args)}")
        print("[!] Direct integration pending - use analysis/elrond.py for now")

    except ImportError:
        print("[ERROR] Elrond module not found")
        print("[*] Use: python3 analysis/elrond.py")
        return 1

    return 0


def cmd_web(args):
    """Start web interface"""
    print("[*] Starting Rivendell web interface...")

    try:
        import uvicorn
        from web.backend.main import app

        host = args.host or "0.0.0.0"
        port = args.port or 8000

        print(f"[+] Starting server on {host}:{port}")
        print(f"[+] API documentation: http://{host}:{port}/docs")

        uvicorn.run(
            "web.backend.main:app",
            host=host,
            port=port,
            reload=args.reload,
            log_level="info"
        )

    except ImportError as e:
        print(f"[ERROR] Failed to import web dependencies: {e}")
        print("[*] Install web dependencies: pip install -r requirements/web.txt")
        return 1

    return 0


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Rivendell - Digital Forensics Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Acquire from local system with encryption
  rivendell acquire Password Local -m -o /evidence

  # Analyze acquired evidence
  rivendell analyze CASE-001 /evidence/hostname.tar.gz /output -CPA

  # Start web interface
  rivendell web --port 8000

  # Use individual tools directly:
  python3 acquisition/python/gandalf.py Password Local -M
  python3 analysis/elrond.py CASE-001 /evidence /output -CPAS
        """
    )

    parser.add_argument('--version', action='version', version=f'Rivendell {VERSION}')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Acquire command (Gandalf)
    acquire_parser = subparsers.add_parser('acquire', help='Acquire forensic artifacts')
    acquire_parser.add_argument('encryption', choices=['Key', 'Password', 'None'],
                               help='Encryption method')
    acquire_parser.add_argument('mode', choices=['Local', 'Remote'],
                               help='Acquisition mode')
    acquire_parser.add_argument('-o', '--output', help='Output directory')
    acquire_parser.add_argument('-m', '--memory', action='store_true',
                               help='Acquire memory dump')
    acquire_parser.add_argument('-a', '--access-times', action='store_true',
                               help='Collect access times')
    acquire_parser.add_argument('-c', '--collect-files', action='store_true',
                               help='Collect specific files')
    acquire_parser.set_defaults(func=cmd_acquire)

    # Analyze command (Elrond)
    analyze_parser = subparsers.add_parser('analyze', help='Analyze forensic artifacts')
    analyze_parser.add_argument('case_id', help='Case identifier')
    analyze_parser.add_argument('evidence_path', help='Path to evidence file/directory')
    analyze_parser.add_argument('output', nargs='?', help='Output directory')
    analyze_parser.add_argument('-C', '--collect', action='store_true',
                               help='Collection phase')
    analyze_parser.add_argument('-P', '--process', action='store_true',
                               help='Processing phase')
    analyze_parser.add_argument('-A', '--analyze', action='store_true',
                               help='Analysis phase')
    analyze_parser.add_argument('-S', '--splunk', action='store_true',
                               help='Export to Splunk')
    analyze_parser.add_argument('-E', '--elastic', action='store_true',
                               help='Export to Elasticsearch')
    analyze_parser.add_argument('-B', '--brisk', action='store_true',
                               help='Brisk mode (quick analysis)')
    analyze_parser.set_defaults(func=cmd_analyze)

    # Web command
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    web_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    web_parser.add_argument('--reload', action='store_true', help='Auto-reload on changes')
    web_parser.set_defaults(func=cmd_web)

    # Parse args
    args = parser.parse_args()

    # Print banner
    print_banner()

    # Execute command
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
