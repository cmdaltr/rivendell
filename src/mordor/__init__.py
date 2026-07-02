"""
Mordor Dataset Management Module

Provides functionality for downloading and managing OTRF Security Datasets
(Mordor datasets) for forensic analysis and threat hunting.

Usage:
    from src.mordor import MordorCatalog, MordorDownloader, MordorStorage

    # List available datasets
    catalog = MordorCatalog()
    datasets = catalog.list_datasets(platform='windows')

    # Download a dataset
    downloader = MordorDownloader()
    result = downloader.download('SDWIN-190518182022')

    # Manage local datasets
    storage = MordorStorage()
    local = storage.list_local_datasets()
"""

from .catalog import MordorCatalog
from .downloader import MordorDownloader
from .storage import MordorStorage
from .models import MordorDataset, DatasetFile, CatalogIndex

__all__ = [
    'MordorCatalog',
    'MordorDownloader',
    'MordorStorage',
    'MordorDataset',
    'DatasetFile',
    'CatalogIndex',
]
