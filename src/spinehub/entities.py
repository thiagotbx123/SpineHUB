"""
SpineHUB Entity Definitions

Defines the core data structures for the knowledge graph:
- Entity: Nodes in the graph (people, projects, channels, topics, teams)
- Relation: Edges connecting entities
- Artifact: Files and documents with URLs
- Pattern: Identified patterns across sessions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib


class EntityType(str, Enum):
    """Types of entities in the knowledge graph."""
    PERSON = "person"
    PROJECT = "project"
    CHANNEL = "channel"
    TOPIC = "topic"
    TEAM = "team"
    FILE = "file"
    API = "api"
    TOOL = "tool"


@dataclass
class Entity:
    """
    A node in the knowledge graph.

    Attributes:
        id: Unique identifier (auto-generated from type + name)
        type: Category of entity (person, project, etc.)
        name: Display name
        metadata: Additional context-specific data
        first_seen: When entity was first discovered
        last_seen: When entity was last referenced
        mention_count: Number of times referenced
    """
    type: EntityType
    name: str
    metadata: dict = field(default_factory=dict)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    mention_count: int = 1
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID from type and name."""
        raw = f"{self.type.value}:{self.name.lower()}"
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "metadata": self.metadata,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "mention_count": self.mention_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Entity":
        """Create Entity from dictionary."""
        return cls(
            id=data.get("id", ""),
            type=EntityType(data["type"]),
            name=data["name"],
            metadata=data.get("metadata", {}),
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            mention_count=data.get("mention_count", 1),
        )


@dataclass
class Relation:
    """
    An edge connecting two entities.

    Attributes:
        source_id: ID of the source entity
        target_id: ID of the target entity
        type: Type of relationship (works_with, owns, mentions, etc.)
        weight: Strength of the relationship (incremented on each interaction)
        context: Additional context about the relationship
        first_seen: When relationship was first established
        last_seen: When relationship was last referenced
    """
    source_id: str
    target_id: str
    type: str
    weight: int = 1
    context: str = ""
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID from source, target, and type."""
        raw = f"{self.source_id}:{self.type}:{self.target_id}"
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "weight": self.weight,
            "context": self.context,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Relation":
        """Create Relation from dictionary."""
        return cls(
            id=data.get("id", ""),
            source_id=data["source_id"],
            target_id=data["target_id"],
            type=data["type"],
            weight=data.get("weight", 1),
            context=data.get("context", ""),
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
        )


@dataclass
class Artifact:
    """
    A file or document tracked in the system.

    Attributes:
        id: Unique identifier
        name: Display name / filename
        type: File type (doc, pdf, xlsx, png, etc.)
        source: Origin (drive, local, slack, etc.)
        url: URL or path to access the artifact
        entity_ids: IDs of entities this artifact relates to
        metadata: Additional metadata (size, modified date, etc.)
        created_at: When artifact was first tracked
    """
    name: str
    type: str
    source: str
    url: str = ""
    entity_ids: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID from source and name."""
        raw = f"{self.source}:{self.name}"
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "source": self.source,
            "url": self.url,
            "entity_ids": self.entity_ids,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        """Create Artifact from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data["name"],
            type=data["type"],
            source=data["source"],
            url=data.get("url", ""),
            entity_ids=data.get("entity_ids", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class Pattern:
    """
    An identified pattern across sessions.

    Attributes:
        id: Unique identifier
        name: Pattern name
        description: What this pattern represents
        frequency: How often this pattern occurs
        entity_ids: Entities involved in this pattern
        examples: Concrete examples of the pattern
        created_at: When pattern was first identified
    """
    name: str
    description: str
    frequency: int = 1
    entity_ids: list = field(default_factory=list)
    examples: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID from name."""
        raw = f"pattern:{self.name.lower()}"
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "entity_ids": self.entity_ids,
            "examples": self.examples,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pattern":
        """Create Pattern from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data["name"],
            description=data["description"],
            frequency=data.get("frequency", 1),
            entity_ids=data.get("entity_ids", []),
            examples=data.get("examples", []),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


def merge_entities(existing: Entity, new: Entity) -> Entity:
    """
    Merge two entity records, preserving history.

    The existing entity is updated with:
    - Merged metadata (new values override)
    - Updated last_seen timestamp
    - Incremented mention_count
    """
    existing.metadata.update(new.metadata)
    existing.last_seen = datetime.now()
    existing.mention_count += 1
    return existing
