"""Pydantic models for Mordor datasets."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class DatasetStatus(str, Enum):
    """Status of a Mordor dataset."""
    AVAILABLE = "available"      # In catalog, not downloaded
    DOWNLOADING = "downloading"  # Currently downloading
    DOWNLOADED = "downloaded"    # Successfully downloaded
    FAILED = "failed"            # Download failed
    VERIFYING = "verifying"      # Checksum verification in progress


class AttackMapping(BaseModel):
    """MITRE ATT&CK technique mapping."""
    technique: str
    sub_technique: Optional[str] = None
    tactics: List[str] = []


class DatasetFile(BaseModel):
    """Individual file in a Mordor dataset."""
    type: str  # "Host", "Network", etc.
    link: str
    local_path: Optional[str] = None
    size: Optional[int] = None
    checksum: Optional[str] = None
    filename: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.filename and self.link:
            self.filename = self.link.split('/')[-1]


class SimulationTool(BaseModel):
    """Tool used in attack simulation."""
    type: str
    name: str
    module: Optional[str] = None
    script: Optional[str] = None


class Simulation(BaseModel):
    """Simulation information for a dataset."""
    environment: Optional[str] = None
    tools: List[SimulationTool] = []
    permissions_required: List[str] = []
    adversary_view: Optional[str] = None


class Contributor(BaseModel):
    """Dataset contributor."""
    name: str
    twitter: Optional[str] = None
    website: Optional[str] = None


class Notebook(BaseModel):
    """Jupyter notebook reference."""
    project: Optional[str] = None
    name: Optional[str] = None
    link: Optional[str] = None


class MordorDataset(BaseModel):
    """Complete Mordor dataset model."""
    dataset_id: str = Field(..., alias="id")
    title: str
    description: Optional[str] = None
    platform: str = "Unknown"
    dataset_type: str = Field(default="atomic", alias="type")

    # MITRE ATT&CK mappings
    attack_mappings: List[AttackMapping] = []
    tactics: List[str] = []  # Derived from attack_mappings
    techniques: List[str] = []  # Derived from attack_mappings

    # Files
    files: List[DatasetFile] = []
    total_size: Optional[int] = None

    # Simulation details
    simulation: Optional[Simulation] = None

    # Metadata
    contributors: List[Contributor] = []
    tags: List[str] = []
    notebooks: List[Notebook] = []
    references: List[str] = []

    # Source info
    source_url: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None

    # Local status (for tracking downloads)
    status: DatasetStatus = DatasetStatus.AVAILABLE
    local_path: Optional[str] = None
    downloaded_at: Optional[datetime] = None
    download_progress: int = 0
    error: Optional[str] = None
    celery_task_id: Optional[str] = None

    class Config:
        populate_by_name = True
        use_enum_values = True

    def derive_tactics_techniques(self):
        """Extract tactics and techniques from attack_mappings."""
        tactics = set()
        techniques = set()
        for mapping in self.attack_mappings:
            techniques.add(mapping.technique)
            tactics.update(mapping.tactics)
        self.tactics = sorted(list(tactics))
        self.techniques = sorted(list(techniques))


class CatalogIndex(BaseModel):
    """Catalog index for caching."""
    last_updated: datetime
    datasets: List[MordorDataset]
    total_count: int
    platforms: Dict[str, int] = {}
    tactics: Dict[str, int] = {}
    techniques: Dict[str, int] = {}

    def compute_statistics(self):
        """Compute platform, tactic, and technique statistics."""
        self.platforms = {}
        self.tactics = {}
        self.techniques = {}

        for ds in self.datasets:
            # Platform count
            self.platforms[ds.platform] = self.platforms.get(ds.platform, 0) + 1

            # Tactics count
            for tactic in ds.tactics:
                self.tactics[tactic] = self.tactics.get(tactic, 0) + 1

            # Techniques count
            for technique in ds.techniques:
                self.techniques[technique] = self.techniques.get(technique, 0) + 1


class DatasetDownloadResult(BaseModel):
    """Result of a dataset download operation."""
    dataset_id: str
    success: bool
    local_path: Optional[str] = None
    files: List[Dict[str, Any]] = []
    total_size: int = 0
    error: Optional[str] = None
    checksum: Optional[str] = None


class DatasetVerifyResult(BaseModel):
    """Result of a dataset verification operation."""
    dataset_id: str
    valid: bool
    files_checked: int = 0
    total_files: int = 0
    errors: List[str] = []
