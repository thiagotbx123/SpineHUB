"""
Tests for SpineHUB core functionality.
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile

from src.spinehub import (
    Entity,
    Relation,
    Artifact,
    EntityType,
    SpineStorage,
    SpineHub,
    QualityValidator,
)


class TestEntities:
    """Test Entity class."""

    def test_entity_creation(self):
        entity = Entity(
            type=EntityType.PERSON,
            name="Thiago",
            metadata={"role": "TSA"},
        )
        assert entity.type == EntityType.PERSON
        assert entity.name == "Thiago"
        assert entity.metadata["role"] == "TSA"
        assert entity.id  # Should auto-generate

    def test_entity_id_consistency(self):
        """Same type+name should generate same ID."""
        e1 = Entity(type=EntityType.PERSON, name="Thiago")
        e2 = Entity(type=EntityType.PERSON, name="Thiago")
        assert e1.id == e2.id

    def test_entity_serialization(self):
        entity = Entity(
            type=EntityType.PROJECT,
            name="TSA_CORTEX",
        )
        data = entity.to_dict()
        restored = Entity.from_dict(data)
        assert restored.name == entity.name
        assert restored.type == entity.type


class TestRelations:
    """Test Relation class."""

    def test_relation_creation(self):
        relation = Relation(
            source_id="abc123",
            target_id="def456",
            type="works_with",
            context="On WFS project",
        )
        assert relation.source_id == "abc123"
        assert relation.target_id == "def456"
        assert relation.weight == 1

    def test_relation_serialization(self):
        relation = Relation(
            source_id="abc",
            target_id="def",
            type="mentions",
        )
        data = relation.to_dict()
        restored = Relation.from_dict(data)
        assert restored.source_id == relation.source_id
        assert restored.type == relation.type


class TestArtifacts:
    """Test Artifact class."""

    def test_artifact_creation(self):
        artifact = Artifact(
            name="report.xlsx",
            type="spreadsheet",
            source="drive",
            url="https://drive.google.com/...",
        )
        assert artifact.name == "report.xlsx"
        assert artifact.type == "spreadsheet"

    def test_artifact_serialization(self):
        artifact = Artifact(
            name="doc.pdf",
            type="pdf",
            source="local",
        )
        data = artifact.to_dict()
        restored = Artifact.from_dict(data)
        assert restored.name == artifact.name


class TestStorage:
    """Test SpineStorage class."""

    def test_storage_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            storage = SpineStorage(str(path))
            assert storage.data["entities"] == {}

    def test_add_entity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            storage = SpineStorage(str(path))

            entity = Entity(type=EntityType.PERSON, name="Test")
            result = storage.add_entity(entity)

            assert result.id in storage.data["entities"]

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            storage = SpineStorage(str(path))

            entity = Entity(type=EntityType.PERSON, name="Test")
            storage.add_entity(entity)
            storage.save()

            # Load fresh
            storage2 = SpineStorage(str(path))
            assert len(storage2.data["entities"]) == 1

    def test_find_entities(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            storage = SpineStorage(str(path))

            storage.add_entity(Entity(type=EntityType.PERSON, name="Alice"))
            storage.add_entity(Entity(type=EntityType.PERSON, name="Bob"))
            storage.add_entity(Entity(type=EntityType.PROJECT, name="Test"))

            people = storage.find_entities(entity_type="person")
            assert len(people) == 2


class TestSpineHub:
    """Test SpineHub class."""

    def test_ingest_slack_message(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub.json"
            hub = SpineHub(str(path))

            result = hub.ingest_slack_message(
                text="Hey @Katherine, can we discuss WFS?",
                channel="project-wfs",
                sender="Thiago",
                timestamp=datetime.now(),
                is_my_work=True,
            )

            assert len(result["entities"]) > 0
            assert len(result["relations"]) > 0

    def test_get_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub.json"
            hub = SpineHub(str(path))

            stats = hub.get_stats()
            assert "entities" in stats
            assert "relations" in stats


class TestQualityValidator:
    """Test QualityValidator class."""

    def test_english_only_pass(self):
        validator = QualityValidator()
        content = "Thiago worked on the WFS project this week."
        results = validator.validate(content)

        lang_result = next(r for r in results if r.rule_id == "LANG_001")
        assert lang_result.passed

    def test_english_only_fail(self):
        validator = QualityValidator()
        content = "Thiago trabalhou no projeto WFS esta semana."
        results = validator.validate(content)

        lang_result = next(r for r in results if r.rule_id == "LANG_001")
        assert not lang_result.passed

    def test_third_person_pass(self):
        validator = QualityValidator()
        content = "Thiago completed the feature implementation."
        results = validator.validate(content)

        pers_result = next(r for r in results if r.rule_id == "PERS_001")
        assert pers_result.passed

    def test_third_person_fail(self):
        validator = QualityValidator()
        content = "I worked on the feature implementation."
        results = validator.validate(content)

        pers_result = next(r for r in results if r.rule_id == "PERS_001")
        assert not pers_result.passed

    def test_summary_section(self):
        validator = QualityValidator()
        content = """
## Summary
This week focused on WFS integration.
"""
        results = validator.validate(content)

        summary_result = next(r for r in results if r.rule_id == "STRUCT_001")
        assert summary_result.passed

    def test_format_report(self):
        validator = QualityValidator()
        content = "Thiago worked on the project."
        validator.validate(content)
        report = validator.format_report()

        assert "QUALITY VALIDATION REPORT" in report
        assert "Status:" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
