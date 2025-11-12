"""
MITRE ATT&CK Integration Module

Provides automatic ATT&CK framework updates, technique mapping,
and dashboard generation for forensic analysis.

Usage:
    from analysis.mitre import MitreAttackUpdater, TechniqueMapper, MitreDashboardGenerator

    # Update ATT&CK data
    updater = MitreAttackUpdater()
    updater.update_local_cache()

    # Map artifacts to techniques
    mapper = TechniqueMapper()
    techniques = mapper.map_artifact_to_techniques('powershell_history', context='invoke-mimikatz')

    # Generate dashboards
    generator = MitreDashboardGenerator()
    generator.save_dashboards(techniques, '/output/dashboards')
"""

from .attck_updater import MitreAttackUpdater
from .technique_mapper import TechniqueMapper, map_artifact
from .dashboard_generator import MitreDashboardGenerator, generate_dashboards

__all__ = [
    'MitreAttackUpdater',
    'TechniqueMapper',
    'MitreDashboardGenerator',
    'map_artifact',
    'generate_dashboards',
]

__version__ = '2.1.0'
