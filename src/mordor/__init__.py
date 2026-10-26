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

import importlib

# Loaded on first use, so src.mordor.telemetry (stdlib only) imports without pydantic
_EXPORTS = {
    'MordorCatalog': '.catalog',
    'MordorDownloader': '.downloader',
    'MordorStorage': '.storage',
    'MordorDataset': '.models',
    'DatasetFile': '.models',
    'CatalogIndex': '.models',
}


def __getattr__(name):
    if name in _EXPORTS:
        return getattr(importlib.import_module(_EXPORTS[name], __name__), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'MordorCatalog',
    'MordorDownloader',
    'MordorStorage',
    'MordorDataset',
    'DatasetFile',
    'CatalogIndex',
]
