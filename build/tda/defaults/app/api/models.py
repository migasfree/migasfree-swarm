"""
Pydantic Models for TDA API Requests & Configurations
"""
from typing import List, Optional, Union
from pydantic import BaseModel, field_validator
from core.config import LENS_COLORS_DEFAULT, DEFAULT_LENS_COLOR, COLOR_KINDS
from lens_store import validate_lens


class LoginRequest(BaseModel):
    username: str
    password: str


class TdaConfig(BaseModel):
    formula_prefix_ids: List[int]
    lens_colors: dict = {}
    metrics_interval_days: Optional[int] = 365

    @field_validator("formula_prefix_ids")
    @classmethod
    def validate_ids(cls, v):
        cleaned = [i for i in v if i > 0]
        if not cleaned:
            raise ValueError("formula_prefix_ids must contain at least one positive integer")
        return cleaned

    @field_validator("lens_colors")
    @classmethod
    def validate_lens_colors(cls, v):
        if not isinstance(v, dict):
            raise ValueError("lens_colors must be an object")
        cleaned = {}
        for lens, entry in v.items():
            if not isinstance(entry, dict):
                continue
            fallback = LENS_COLORS_DEFAULT.get(lens, DEFAULT_LENS_COLOR)
            columns = entry.get("columns")
            if not columns:
                columns = fallback["columns"]
            elif isinstance(columns, (list, tuple)):
                columns = [str(c) for c in columns if str(c).strip()]
            else:
                columns = [str(columns)]
            if not columns:
                columns = fallback["columns"]

            entry_kind = entry.get("kind")
            if entry_kind is not None and str(entry_kind) in COLOR_KINDS:
                kind = str(entry_kind)
            elif "project_encoded" in columns:
                kind = "categorical"
            else:
                kind = str(fallback.get("kind") or "continuous")
            cleaned[lens] = {
                "columns": list(columns),
                "label": str(entry.get("label") or fallback["label"]),
                "kind": kind,
            }
        return cleaned


class LensColor(BaseModel):
    columns: List[str] = []
    label: str = ""
    kind: str = "continuous"


class LensDataset(BaseModel):
    formula_prefix_ids: List[int] = []
    scope_ids: List[int] = []
    metric_columns: Optional[List[str]] = None


class LensSection(BaseModel):
    type: str = "pca"
    components: int = 2
    metric_columns: List[str] = []
    matrix_source: Optional[str] = None


class CoverSection(BaseModel):
    type: str = "cubical"
    n_cubes: Optional[int] = None
    overlap: Optional[float] = None
    radius: Optional[float] = None
    n_neighbors: Optional[int] = None


class ClusteringSection(BaseModel):
    scaling: bool = True
    type: str = "dbscan"
    n_clusters: Optional[int] = None
    eps: Optional[float] = None
    min_samples: Optional[int] = None


class DrawSection(BaseModel):
    dimensions: int = 3
    iterations: Optional[int] = None
    seed: Optional[int] = None
    color: Optional[LensColor] = None
    node_label: str = "attribute"


class LensSpec(BaseModel):
    name: str
    label: str
    description: str = ""
    lens: Optional[LensSection] = None
    cover: Optional[CoverSection] = None
    clustering: Optional[ClusteringSection] = None
    draw: Optional[DrawSection] = None
    dataset: Optional[LensDataset] = None
    builtin: bool = False

    def to_descriptor(self, current_name=None) -> dict:
        """Validate and normalize into a lens_store descriptor."""
        raw = {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "lens": self.lens.model_dump() if self.lens else None,
            "cover": self.cover.model_dump() if self.cover else None,
            "clustering": self.clustering.model_dump() if self.clustering else None,
            "draw": self.draw.model_dump() if self.draw else None,
            "dataset": self.dataset.model_dump() if self.dataset else None,
            "builtin": self.builtin,
        }
        return validate_lens(raw, current_name=current_name)
