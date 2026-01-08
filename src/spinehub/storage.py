"""
SpineHUB Storage Layer

JSON-based persistence with atomic saves and backup support.
Handles all CRUD operations for entities, relations, artifacts, and patterns.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from .entities import Entity, Relation, Artifact, Pattern


class SpineStorage:
    """
    JSON-based storage for SpineHUB data.

    Features:
    - Atomic saves (write to temp, then rename)
    - Automatic backups before each save
    - Lazy loading (data loaded on first access)
    - Index maintenance for fast lookups
    """

    def __init__(self, data_path: str = "data/spinehub.json"):
        self.data_path = Path(data_path)
        self.backup_dir = self.data_path.parent / "backups"
        self._data: Optional[dict] = None
        self._dirty = False

    @property
    def data(self) -> dict:
        """Lazy-load data on first access."""
        if self._data is None:
            self._load()
        return self._data

    def _load(self) -> None:
        """Load data from JSON file."""
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                self._data = {
                    "entities": {
                        k: Entity.from_dict(v)
                        for k, v in raw.get("entities", {}).items()
                    },
                    "relations": {
                        k: Relation.from_dict(v)
                        for k, v in raw.get("relations", {}).items()
                    },
                    "artifacts": {
                        k: Artifact.from_dict(v)
                        for k, v in raw.get("artifacts", {}).items()
                    },
                    "patterns": {
                        k: Pattern.from_dict(v)
                        for k, v in raw.get("patterns", {}).items()
                    },
                    "metadata": raw.get("metadata", self._default_metadata()),
                }
        else:
            self._data = self._empty_data()

    def _empty_data(self) -> dict:
        """Return empty data structure."""
        return {
            "entities": {},
            "relations": {},
            "artifacts": {},
            "patterns": {},
            "metadata": self._default_metadata(),
        }

    def _default_metadata(self) -> dict:
        """Return default metadata."""
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "stats": {
                "total_entities": 0,
                "total_relations": 0,
                "total_artifacts": 0,
                "total_patterns": 0,
            },
        }

    def save(self, create_backup: bool = True) -> None:
        """
        Save data to JSON file with atomic write.

        Args:
            create_backup: If True, backup existing file before overwriting
        """
        if self._data is None:
            return

        # Ensure directories exist
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if file exists
        if create_backup and self.data_path.exists():
            self._create_backup()

        # Update metadata
        self._data["metadata"]["last_updated"] = datetime.now().isoformat()
        self._data["metadata"]["stats"] = {
            "total_entities": len(self._data["entities"]),
            "total_relations": len(self._data["relations"]),
            "total_artifacts": len(self._data["artifacts"]),
            "total_patterns": len(self._data["patterns"]),
        }

        # Serialize data
        serialized = {
            "entities": {k: v.to_dict() for k, v in self._data["entities"].items()},
            "relations": {k: v.to_dict() for k, v in self._data["relations"].items()},
            "artifacts": {k: v.to_dict() for k, v in self._data["artifacts"].items()},
            "patterns": {k: v.to_dict() for k, v in self._data["patterns"].items()},
            "metadata": self._data["metadata"],
        }

        # Atomic write: write to temp file, then rename
        temp_path = self.data_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)

        # Rename temp to final (atomic on most systems)
        shutil.move(str(temp_path), str(self.data_path))
        self._dirty = False

    def _create_backup(self) -> None:
        """Create a timestamped backup of current data."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"spinehub_{timestamp}.json"
        shutil.copy2(str(self.data_path), str(backup_path))

        # Keep only last 10 backups
        backups = sorted(self.backup_dir.glob("spinehub_*.json"))
        for old_backup in backups[:-10]:
            old_backup.unlink()

    # Entity operations
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.data["entities"].get(entity_id)

    def add_entity(self, entity: Entity) -> Entity:
        """Add or update entity."""
        existing = self.data["entities"].get(entity.id)
        if existing:
            # Merge with existing
            existing.metadata.update(entity.metadata)
            existing.last_seen = datetime.now()
            existing.mention_count += 1
            self._dirty = True
            return existing
        else:
            self.data["entities"][entity.id] = entity
            self._dirty = True
            return entity

    def find_entities(
        self,
        entity_type: Optional[str] = None,
        name_contains: Optional[str] = None,
    ) -> list[Entity]:
        """Find entities matching criteria."""
        results = []
        for entity in self.data["entities"].values():
            if entity_type and entity.type.value != entity_type:
                continue
            if name_contains and name_contains.lower() not in entity.name.lower():
                continue
            results.append(entity)
        return results

    # Relation operations
    def get_relation(self, relation_id: str) -> Optional[Relation]:
        """Get relation by ID."""
        return self.data["relations"].get(relation_id)

    def add_relation(self, relation: Relation) -> Relation:
        """Add or update relation."""
        existing = self.data["relations"].get(relation.id)
        if existing:
            existing.weight += 1
            existing.last_seen = datetime.now()
            if relation.context:
                existing.context = relation.context
            self._dirty = True
            return existing
        else:
            self.data["relations"][relation.id] = relation
            self._dirty = True
            return relation

    def find_relations(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[str] = None,
    ) -> list[Relation]:
        """Find relations matching criteria."""
        results = []
        for relation in self.data["relations"].values():
            if source_id and relation.source_id != source_id:
                continue
            if target_id and relation.target_id != target_id:
                continue
            if relation_type and relation.type != relation_type:
                continue
            results.append(relation)
        return results

    # Artifact operations
    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Get artifact by ID."""
        return self.data["artifacts"].get(artifact_id)

    def add_artifact(self, artifact: Artifact) -> Artifact:
        """Add or update artifact."""
        existing = self.data["artifacts"].get(artifact.id)
        if existing:
            existing.metadata.update(artifact.metadata)
            if artifact.url:
                existing.url = artifact.url
            existing.entity_ids = list(set(existing.entity_ids + artifact.entity_ids))
            self._dirty = True
            return existing
        else:
            self.data["artifacts"][artifact.id] = artifact
            self._dirty = True
            return artifact

    def find_artifacts(
        self,
        source: Optional[str] = None,
        artifact_type: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> list[Artifact]:
        """Find artifacts matching criteria."""
        results = []
        for artifact in self.data["artifacts"].values():
            if source and artifact.source != source:
                continue
            if artifact_type and artifact.type != artifact_type:
                continue
            if entity_id and entity_id not in artifact.entity_ids:
                continue
            results.append(artifact)
        return results

    # Pattern operations
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get pattern by ID."""
        return self.data["patterns"].get(pattern_id)

    def add_pattern(self, pattern: Pattern) -> Pattern:
        """Add or update pattern."""
        existing = self.data["patterns"].get(pattern.id)
        if existing:
            existing.frequency += 1
            existing.entity_ids = list(set(existing.entity_ids + pattern.entity_ids))
            existing.examples = list(set(existing.examples + pattern.examples))[:10]
            self._dirty = True
            return existing
        else:
            self.data["patterns"][pattern.id] = pattern
            self._dirty = True
            return pattern

    # Stats and metadata
    def get_stats(self) -> dict:
        """Get current statistics."""
        return {
            "entities": len(self.data["entities"]),
            "relations": len(self.data["relations"]),
            "artifacts": len(self.data["artifacts"]),
            "patterns": len(self.data["patterns"]),
            "metadata": self.data["metadata"],
        }

    def clear(self) -> None:
        """Clear all data (with backup)."""
        if self.data_path.exists():
            self._create_backup()
        self._data = self._empty_data()
        self._dirty = True
