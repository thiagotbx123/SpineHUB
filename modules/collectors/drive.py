"""
Google Drive Collector - Collects files and metadata from Google Drive

Ported from GOD_EXTRACT JavaScript implementation.
Uses Google Drive API to inventory and classify files.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import (
    BaseCollector,
    CollectorResult,
    ActivityEvent,
    SourcePointer,
    SourceSystem,
    EventType,
    OwnershipType,
)


class DriveCollector(BaseCollector):
    """
    Collector for Google Drive file activity.

    Features:
    - Recursive folder traversal
    - File classification by relevance, doc role, confidentiality
    - Modified files within date range
    - Metadata extraction
    """

    # Classification patterns
    HIGH_RELEVANCE_PATTERNS = [
        "strategy", "roadmap", "sow", "msa", "dpa", "contract", "pricing",
        "okr", "kpi", "soc", "security", "onboarding", "playbook", "master",
        "tracker", "template", "process", "architecture", "decision", "plan"
    ]

    MEDIUM_RELEVANCE_PATTERNS = [
        "proposal", "scope", "requirement", "spec", "design", "review",
        "notes", "meeting", "checklist", "guide", "training", "demo"
    ]

    # MIME type mapping
    MIME_MAP = {
        "application/vnd.google-apps.document": "gdoc",
        "application/vnd.google-apps.spreadsheet": "gsheet",
        "application/vnd.google-apps.presentation": "gslides",
        "application/vnd.google-apps.form": "gform",
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
        "text/plain": "txt",
        "text/csv": "csv",
        "image/png": "png",
        "image/jpeg": "jpg",
        "application/json": "json",
    }

    def __init__(
        self,
        config: Dict[str, Any],
        date_range: tuple[datetime, datetime],
        user_id: Optional[str] = None,
    ):
        super().__init__(config, date_range, user_id)

        self.client_id = config.get("GOOGLE_CLIENT_ID") or os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = config.get("GOOGLE_CLIENT_SECRET") or os.getenv("GOOGLE_CLIENT_SECRET")
        self.refresh_token = config.get("GOOGLE_REFRESH_TOKEN") or os.getenv("GOOGLE_REFRESH_TOKEN")

        # Folder IDs to scan (can be overridden in config)
        self.folder_ids: List[str] = config.get("DRIVE_FOLDER_IDS", [])

        # Caches
        self._folder_cache: Dict[str, str] = {}
        self._drive_service = None

    @property
    def source(self) -> str:
        return SourceSystem.DRIVE.value

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    async def collect(self) -> CollectorResult:
        result = self.create_empty_result()

        if not self.is_configured():
            result.errors.append("Google Drive credentials not configured")
            return result

        try:
            # Import Google API client
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
            except ImportError:
                result.errors.append(
                    "Google API client required. Install with: pip install google-api-python-client google-auth"
                )
                return result

            # Build credentials
            creds = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
            )

            # Build service
            self._drive_service = build("drive", "v3", credentials=creds)
            self.log_info("Drive service initialized")

            # Collect from each folder
            all_files: List[Dict] = []

            if not self.folder_ids:
                # Use root folder if no specific folders configured
                self.folder_ids = ["root"]

            for folder_id in self.folder_ids:
                folder_name = await self._get_folder_name(folder_id)
                self.log_info(f"Scanning folder: {folder_name}")

                files = await self._list_files_in_folder(folder_id, folder_name)
                all_files.extend(files)

            self.log_info(f"Found {len(all_files)} files total")

            # Filter by date range
            filtered_files = []
            for file in all_files:
                modified_time = file.get("modifiedTime", "")
                if modified_time:
                    try:
                        modified_dt = datetime.fromisoformat(modified_time.replace("Z", "+00:00"))
                        if self.is_within_date_range(modified_dt):
                            filtered_files.append(file)
                    except ValueError:
                        pass

            self.log_info(f"Files modified in date range: {len(filtered_files)}")

            result.raw_data = filtered_files

            # Transform to events
            for file in filtered_files:
                event = self._transform_file(file)
                if event:
                    result.events.append(event)

            self.log_info(f"Collected {len(result.events)} events from Drive")

        except Exception as e:
            result.errors.append(f"Drive collection failed: {str(e)}")

        return result

    async def _get_folder_name(self, folder_id: str) -> str:
        """Get folder name by ID."""
        if folder_id == "root":
            return "My Drive"

        if folder_id in self._folder_cache:
            return self._folder_cache[folder_id]

        try:
            response = self._drive_service.files().get(
                fileId=folder_id,
                fields="name",
                supportsAllDrives=True,
            ).execute()
            name = response.get("name", folder_id)
            self._folder_cache[folder_id] = name
            return name
        except Exception as e:
            self.log_warn(f"Could not get folder name for {folder_id}: {e}")
            return folder_id

    async def _list_files_in_folder(
        self,
        folder_id: str,
        folder_path: str = ""
    ) -> List[Dict]:
        """Recursively list files in a folder."""
        files = []
        page_token = None

        while True:
            try:
                response = self._drive_service.files().list(
                    q=f"'{folder_id}' in parents and trashed = false",
                    fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, webViewLink, owners, size, parents)",
                    pageSize=100,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                ).execute()

                for file in response.get("files", []):
                    file_name = file.get("name", "")
                    file_path = f"{folder_path}/{file_name}" if folder_path else file_name

                    # If it's a folder, recurse
                    if file.get("mimeType") == "application/vnd.google-apps.folder":
                        self.log_info(f"[FOLDER] {file_path}")
                        sub_files = await self._list_files_in_folder(file["id"], file_path)
                        files.extend(sub_files)
                    else:
                        # Add file with path info
                        file["folderPath"] = folder_path
                        file["fullPath"] = file_path
                        file["ownerEmail"] = file.get("owners", [{}])[0].get("emailAddress", "unknown")
                        file["ownerName"] = file.get("owners", [{}])[0].get("displayName", "Unknown")
                        files.append(file)

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            except Exception as e:
                self.log_error(f"Failed to list files in {folder_id}: {e}")
                break

        return files

    def _classify_file(self, file: Dict) -> Dict[str, Any]:
        """Classify file by relevance, doc role, and confidentiality."""
        name = file.get("name", "").lower()
        path = file.get("fullPath", "").lower()

        # Relevance scoring
        relevance = "low"
        if any(p in name or p in path for p in self.HIGH_RELEVANCE_PATTERNS):
            relevance = "high"
        elif any(p in name or p in path for p in self.MEDIUM_RELEVANCE_PATTERNS):
            relevance = "medium"

        # Doc role classification
        doc_role = "other"
        role_patterns = {
            "contract": r"sow|msa|dpa|nda|contract|agreement",
            "strategy": r"strategy|okr|kpi|north.?star",
            "roadmap": r"roadmap|backlog|epic",
            "customer": r"customer|client|account",
            "security": r"security|soc|audit|compliance",
            "finance": r"finance|pricing|billing|cost",
            "process": r"process|playbook|sop|runbook",
            "engineering": r"engineering|architecture|technical",
            "marketing": r"marketing|messaging|positioning",
            "sales": r"sales|demo|pitch",
            "enablement": r"enablement|training|onboard",
            "hiring": r"hiring|recruiting|culture",
        }

        import re
        for role, pattern in role_patterns.items():
            if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, path, re.IGNORECASE):
                doc_role = role
                break

        # Confidentiality
        confidentiality = "internal"
        if re.search(r"confidential|private|secret|sensitive", name, re.IGNORECASE):
            confidentiality = "confidential"
        elif re.search(r"public|external|shared", path, re.IGNORECASE):
            confidentiality = "internal_public"

        # Topic tags
        tags = []
        tag_patterns = [
            ("company", r"testbox"),
            ("intuit", r"intuit|quickbooks|qbo"),
            ("strategy", r"strategy|plan"),
            ("product", r"product"),
            ("demo", r"demo|scenario"),
            ("pricing", r"pricing"),
            ("contract", r"sow|contract"),
            ("security", r"security|soc"),
            ("dataset", r"data|dataset"),
            ("api", r"api|integration"),
        ]

        for tag, pattern in tag_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                tags.append(tag)

        return {
            "relevance": relevance,
            "doc_role": doc_role,
            "confidentiality": confidentiality,
            "topic_tags": list(set(tags)),
        }

    def _get_file_type(self, mime_type: str) -> str:
        """Get file type from MIME type."""
        return self.MIME_MAP.get(mime_type, mime_type.split("/")[-1])

    def _transform_file(self, file: Dict) -> Optional[ActivityEvent]:
        """Transform Drive file to ActivityEvent."""
        modified_time = file.get("modifiedTime", "")
        if not modified_time:
            return None

        try:
            modified_dt = datetime.fromisoformat(modified_time.replace("Z", "+00:00"))
        except ValueError:
            return None

        classification = self._classify_file(file)
        file_type = self._get_file_type(file.get("mimeType", ""))

        return ActivityEvent(
            event_id=self.generate_event_id("drive", file.get("id", ""), modified_time),
            source_system=SourceSystem.DRIVE,
            event_type=EventType.FILE_MODIFIED,
            event_timestamp=modified_dt,
            title=file.get("name", "Unknown file"),
            body_text=f"Modified in {file.get('folderPath', 'root')}",
            actor_name=file.get("ownerName", "Unknown"),
            ownership=OwnershipType.CONTEXT,
            confidence="medium",
            source_pointers=[
                SourcePointer(
                    pointer_id=self.generate_pointer_id("drive_file", file.get("id", "")),
                    type="drive_file_url",
                    url=file.get("webViewLink", ""),
                    display_text=file.get("name", ""),
                )
            ],
            metadata={
                "file_type": file_type,
                "folder_path": file.get("folderPath", ""),
                "size_bytes": file.get("size"),
                "owner_email": file.get("ownerEmail"),
                "relevance": classification["relevance"],
                "doc_role": classification["doc_role"],
                "confidentiality": classification["confidentiality"],
                "topic_tags": classification["topic_tags"],
            },
        )
