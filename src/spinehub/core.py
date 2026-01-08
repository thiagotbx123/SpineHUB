"""
SpineHUB Core Engine

Main class that orchestrates the knowledge graph operations:
- Entity extraction from various sources
- Relation inference
- Artifact tracking
- Pattern detection
- Narrative context generation
"""

import re
from datetime import datetime
from typing import Optional

from .entities import Entity, Relation, Artifact, EntityType
from .storage import SpineStorage


class SpineHub:
    """
    Main SpineHUB engine for knowledge graph management.

    Provides high-level methods for:
    - Ingesting data from various sources
    - Querying the knowledge graph
    - Generating narrative context
    - Identifying collaboration patterns
    """

    # Known people patterns for entity extraction
    KNOWN_PEOPLE_PATTERNS = [
        r"\b(Thiago|Katherine|Kat|Alexandra|Diego|Gabrielle|Lucas|Josh|Christina)\b",
    ]

    # Project keywords for topic inference
    PROJECT_KEYWORDS = {
        "wfs": ["wfs", "workforce", "goco", "payroll", "hr"],
        "tco": ["tco", "apex", "tire", "consolidated"],
        "construction": ["construction", "keystone", "certified payroll"],
        "gem": ["gem", "recruiting", "ats", "candidate"],
        "fall_release": ["fall release", "winter release", "feature", "validation"],
    }

    def __init__(self, storage_path: str = "data/spinehub.json"):
        self.storage = SpineStorage(storage_path)

    # =========================================
    # INGESTION METHODS
    # =========================================

    def ingest_slack_message(
        self,
        text: str,
        channel: str,
        sender: str,
        timestamp: datetime,
        is_my_work: bool = False,
    ) -> dict:
        """
        Ingest a Slack message into the knowledge graph.

        Returns dict with created/updated entities and relations.
        """
        results = {"entities": [], "relations": [], "artifacts": []}

        # Create channel entity
        channel_entity = Entity(
            type=EntityType.CHANNEL,
            name=channel,
            metadata={"source": "slack"},
        )
        self.storage.add_entity(channel_entity)
        results["entities"].append(channel_entity)

        # Create sender entity
        sender_entity = Entity(
            type=EntityType.PERSON,
            name=sender,
            metadata={"source": "slack", "is_my_work": is_my_work},
        )
        self.storage.add_entity(sender_entity)
        results["entities"].append(sender_entity)

        # Create relation: sender -> channel
        relation = Relation(
            source_id=sender_entity.id,
            target_id=channel_entity.id,
            type="posts_in",
            context=f"Message at {timestamp.isoformat()}",
        )
        self.storage.add_relation(relation)
        results["relations"].append(relation)

        # Extract mentioned people
        for person in self._extract_people(text):
            person_entity = Entity(
                type=EntityType.PERSON,
                name=person,
                metadata={"source": "slack_mention"},
            )
            self.storage.add_entity(person_entity)
            results["entities"].append(person_entity)

            # Create relation: sender -> mentioned person
            mention_relation = Relation(
                source_id=sender_entity.id,
                target_id=person_entity.id,
                type="mentions",
                context=f"In {channel}",
            )
            self.storage.add_relation(mention_relation)
            results["relations"].append(mention_relation)

        # Extract topics
        for topic in self._infer_topics(text):
            topic_entity = Entity(
                type=EntityType.TOPIC,
                name=topic,
                metadata={"source": "inferred"},
            )
            self.storage.add_entity(topic_entity)
            results["entities"].append(topic_entity)

            # Create relation: channel -> topic
            topic_relation = Relation(
                source_id=channel_entity.id,
                target_id=topic_entity.id,
                type="discusses",
            )
            self.storage.add_relation(topic_relation)
            results["relations"].append(topic_relation)

        # Extract URLs as artifacts
        for url in self._extract_urls(text):
            artifact = Artifact(
                name=url.split("/")[-1] or "link",
                type="url",
                source="slack",
                url=url,
                entity_ids=[channel_entity.id, sender_entity.id],
            )
            self.storage.add_artifact(artifact)
            results["artifacts"].append(artifact)

        return results

    def ingest_drive_file(
        self,
        name: str,
        url: str,
        mime_type: str,
        modified_time: datetime,
        owner: Optional[str] = None,
    ) -> dict:
        """
        Ingest a Google Drive file into the knowledge graph.
        """
        results = {"entities": [], "relations": [], "artifacts": []}

        # Determine file type
        file_type = self._get_file_type(mime_type, name)

        # Create artifact
        entity_ids = []

        if owner:
            owner_entity = Entity(
                type=EntityType.PERSON,
                name=owner,
                metadata={"source": "drive"},
            )
            self.storage.add_entity(owner_entity)
            results["entities"].append(owner_entity)
            entity_ids.append(owner_entity.id)

        # Infer project from filename
        for project in self._infer_topics(name):
            project_entity = Entity(
                type=EntityType.PROJECT,
                name=project,
                metadata={"source": "inferred"},
            )
            self.storage.add_entity(project_entity)
            results["entities"].append(project_entity)
            entity_ids.append(project_entity.id)

        artifact = Artifact(
            name=name,
            type=file_type,
            source="drive",
            url=url,
            entity_ids=entity_ids,
            metadata={"mime_type": mime_type, "modified": modified_time.isoformat()},
        )
        self.storage.add_artifact(artifact)
        results["artifacts"].append(artifact)

        return results

    def ingest_linear_issue(
        self,
        identifier: str,
        title: str,
        url: str,
        state: str,
        assignee: Optional[str] = None,
        labels: Optional[list] = None,
    ) -> dict:
        """
        Ingest a Linear issue into the knowledge graph.
        """
        results = {"entities": [], "relations": [], "artifacts": []}

        # Create artifact for the issue
        entity_ids = []

        if assignee:
            assignee_entity = Entity(
                type=EntityType.PERSON,
                name=assignee,
                metadata={"source": "linear"},
            )
            self.storage.add_entity(assignee_entity)
            results["entities"].append(assignee_entity)
            entity_ids.append(assignee_entity.id)

        # Infer project from title and labels
        for topic in self._infer_topics(title):
            topic_entity = Entity(
                type=EntityType.PROJECT,
                name=topic,
                metadata={"source": "linear"},
            )
            self.storage.add_entity(topic_entity)
            results["entities"].append(topic_entity)
            entity_ids.append(topic_entity.id)

        artifact = Artifact(
            name=f"{identifier}: {title}",
            type="ticket",
            source="linear",
            url=url,
            entity_ids=entity_ids,
            metadata={"state": state, "labels": labels or []},
        )
        self.storage.add_artifact(artifact)
        results["artifacts"].append(artifact)

        return results

    # =========================================
    # QUERY METHODS
    # =========================================

    def get_narrative_context(
        self,
        topic: Optional[str] = None,
        person: Optional[str] = None,
        limit: int = 20,
    ) -> dict:
        """
        Get context for narrative generation.

        Returns entities, relations, and artifacts relevant to the query.
        """
        context = {
            "entities": [],
            "relations": [],
            "artifacts": [],
            "themes": [],
        }

        # Get relevant entities
        if person:
            entities = self.storage.find_entities(name_contains=person)
        elif topic:
            entities = self.storage.find_entities(name_contains=topic)
        else:
            # Get most mentioned entities
            all_entities = list(self.storage.data["entities"].values())
            entities = sorted(all_entities, key=lambda e: -e.mention_count)[:limit]

        context["entities"] = [e.to_dict() for e in entities]

        # Get relations involving these entities
        entity_ids = {e.id for e in entities}
        for relation in self.storage.data["relations"].values():
            if relation.source_id in entity_ids or relation.target_id in entity_ids:
                context["relations"].append(relation.to_dict())
                if len(context["relations"]) >= limit * 2:
                    break

        # Get artifacts
        for entity_id in list(entity_ids)[:5]:
            artifacts = self.storage.find_artifacts(entity_id=entity_id)
            context["artifacts"].extend([a.to_dict() for a in artifacts[:5]])

        # Identify themes
        context["themes"] = self._identify_themes(entities)

        return context

    def get_collaboration_map(self, person: Optional[str] = None) -> dict:
        """
        Get collaboration patterns between people.

        Returns a map of who works with whom and how often.
        """
        collaborations = {}

        # Find person entity if specified
        person_id = None
        if person:
            matches = self.storage.find_entities(
                entity_type="person", name_contains=person
            )
            if matches:
                person_id = matches[0].id

        # Analyze relations
        for relation in self.storage.data["relations"].values():
            if relation.type in ("works_with", "mentions", "collaborates"):
                source = self.storage.get_entity(relation.source_id)
                target = self.storage.get_entity(relation.target_id)

                if not source or not target:
                    continue

                if person_id and person_id not in (source.id, target.id):
                    continue

                key = tuple(sorted([source.name, target.name]))
                if key not in collaborations:
                    collaborations[key] = {
                        "people": list(key),
                        "interactions": 0,
                        "contexts": [],
                    }
                collaborations[key]["interactions"] += relation.weight
                if relation.context:
                    collaborations[key]["contexts"].append(relation.context)

        # Sort by interactions
        return dict(
            sorted(collaborations.items(), key=lambda x: -x[1]["interactions"])
        )

    def get_project_summary(self, project_name: str) -> dict:
        """
        Get summary of a project including related entities and artifacts.
        """
        summary = {
            "project": project_name,
            "people": [],
            "channels": [],
            "artifacts": [],
            "activity_count": 0,
        }

        # Find project entity
        projects = self.storage.find_entities(name_contains=project_name)
        if not projects:
            return summary

        project_id = projects[0].id

        # Find related entities via relations
        for relation in self.storage.data["relations"].values():
            if relation.source_id == project_id or relation.target_id == project_id:
                other_id = (
                    relation.target_id
                    if relation.source_id == project_id
                    else relation.source_id
                )
                entity = self.storage.get_entity(other_id)
                if entity:
                    if entity.type == EntityType.PERSON:
                        summary["people"].append(entity.name)
                    elif entity.type == EntityType.CHANNEL:
                        summary["channels"].append(entity.name)
                summary["activity_count"] += relation.weight

        # Find related artifacts
        artifacts = self.storage.find_artifacts(entity_id=project_id)
        summary["artifacts"] = [
            {"name": a.name, "url": a.url, "type": a.type} for a in artifacts
        ]

        # Deduplicate
        summary["people"] = list(set(summary["people"]))
        summary["channels"] = list(set(summary["channels"]))

        return summary

    # =========================================
    # HELPER METHODS
    # =========================================

    def _extract_people(self, text: str) -> list[str]:
        """Extract mentioned people from text."""
        people = []
        for pattern in self.KNOWN_PEOPLE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            people.extend(matches)
        return list(set(people))

    def _extract_urls(self, text: str) -> list[str]:
        """Extract URLs from text."""
        url_pattern = r"https?://[^\s<>\"']+|www\.[^\s<>\"']+"
        return re.findall(url_pattern, text)

    def _infer_topics(self, text: str) -> list[str]:
        """Infer topics/projects from text using keywords."""
        topics = []
        text_lower = text.lower()
        for topic, keywords in self.PROJECT_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        return topics

    def _get_file_type(self, mime_type: str, name: str) -> str:
        """Determine file type from MIME type and name."""
        if "spreadsheet" in mime_type or name.endswith((".xlsx", ".csv")):
            return "spreadsheet"
        elif "document" in mime_type or name.endswith((".docx", ".doc")):
            return "document"
        elif "presentation" in mime_type or name.endswith((".pptx", ".ppt")):
            return "presentation"
        elif "pdf" in mime_type or name.endswith(".pdf"):
            return "pdf"
        elif "image" in mime_type or name.endswith((".png", ".jpg", ".jpeg")):
            return "image"
        else:
            return "file"

    def _identify_themes(self, entities: list[Entity]) -> list[str]:
        """Identify themes from a list of entities."""
        themes = []
        for entity in entities:
            if entity.type in (EntityType.TOPIC, EntityType.PROJECT):
                themes.append(entity.name)
        return list(set(themes))

    # =========================================
    # PERSISTENCE
    # =========================================

    def save(self) -> None:
        """Save all data to storage."""
        self.storage.save()

    def get_stats(self) -> dict:
        """Get current statistics."""
        return self.storage.get_stats()
