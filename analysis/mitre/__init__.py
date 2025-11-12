"""
MITRE ATT&CK Integration Module

Provides automatic ATT&CK framework updates, technique mapping,
dashboard generation, and real-time coverage analysis for forensic analysis.

Usage:
    # Feature 1: ATT&CK Updates and Mapping
    from analysis.mitre import MitreAttackUpdater, TechniqueMapper, MitreDashboardGenerator

    updater = MitreAttackUpdater()
    updater.update_local_cache()

    mapper = TechniqueMapper()
    techniques = mapper.map_artifact_to_techniques('powershell_history', context='invoke-mimikatz')

    generator = MitreDashboardGenerator()
    generator.save_dashboards(techniques, '/output/dashboards')

    # Feature 2: Real-time Coverage Analysis
    from analysis.mitre import MitreCoverageAnalyzer, generate_standalone_dashboard

    analyzer = MitreCoverageAnalyzer('CASE-001', '/output')
    analyzer.analyze_artifact('powershell_history', '/evidence/ps.txt', context='...')
    report = analyzer.generate_coverage_report()

    dashboard_path = generate_standalone_dashboard(report, '/output/coverage.html')
"""

from .attck_updater import MitreAttackUpdater
from .technique_mapper import TechniqueMapper, map_artifact
from .dashboard_generator import MitreDashboardGenerator, generate_dashboards
from .coverage_analyzer import MitreCoverageAnalyzer, CoverageDatabase, analyze_artifact
from .standalone_dashboard import StandaloneDashboard, generate_standalone_dashboard

__all__ = [
    # Feature 1: ATT&CK Updates and Mapping
    'MitreAttackUpdater',
    'TechniqueMapper',
    'MitreDashboardGenerator',
    'map_artifact',
    'generate_dashboards',
    # Feature 2: Coverage Analysis
    'MitreCoverageAnalyzer',
    'CoverageDatabase',
    'StandaloneDashboard',
    'analyze_artifact',
    'generate_standalone_dashboard',
]

__version__ = '2.1.0'
