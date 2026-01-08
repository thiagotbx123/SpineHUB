"""
Linear Collector - Collects issues, comments, and activity from Linear

Ported from TSA_CORTEX TypeScript implementation.
Uses Linear API to collect issues created, assigned, or commented on by user.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    httpx = None

from .base import (
    BaseCollector,
    CollectorResult,
    ActivityEvent,
    SourcePointer,
    SourceSystem,
    EventType,
    OwnershipType,
)


class LinearCollector(BaseCollector):
    """
    Collector for Linear issue tracking data.

    Collects:
    - Issues created by user
    - Issues assigned to user
    - Issues where user commented
    - Comment history on collected issues
    """

    API_URL = "https://api.linear.app/graphql"

    def __init__(
        self,
        config: Dict[str, Any],
        date_range: tuple[datetime, datetime],
        user_id: Optional[str] = None,
    ):
        super().__init__(config, date_range, user_id)
        self.api_key = config.get("LINEAR_API_KEY") or os.getenv("LINEAR_API_KEY")
        self._viewer_id: Optional[str] = None
        self._viewer_name: Optional[str] = None

    @property
    def source(self) -> str:
        return SourceSystem.LINEAR.value

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def collect(self) -> CollectorResult:
        result = self.create_empty_result()

        if not self.is_configured():
            result.errors.append("Linear API key not configured")
            return result

        if httpx is None:
            result.errors.append("httpx package required for Linear collector. Install with: pip install httpx")
            return result

        try:
            # Get current user
            viewer = await self._get_viewer()
            if not viewer:
                result.errors.append("Failed to get Linear user info")
                return result

            self._viewer_id = viewer.get("id")
            self._viewer_name = viewer.get("name", "Unknown")
            self.log_info(f"Collecting Linear data for: {self._viewer_name}")

            # Collect issues from different relationships
            created_issues = await self._get_issues_created_by()
            self.log_info(f"Found {len(created_issues)} issues created by user")

            assigned_issues = await self._get_issues_assigned_to()
            self.log_info(f"Found {len(assigned_issues)} issues assigned to user")

            commented_issues = await self._get_issues_commented_on()
            self.log_info(f"Found {len(commented_issues)} issues with user comments")

            # Deduplicate by issue ID
            all_issues = self._deduplicate_issues(
                created_issues + assigned_issues + commented_issues
            )

            result.raw_data = all_issues

            # Transform to events
            for issue in all_issues:
                events = self._transform_issue(issue)
                result.events.extend(events)

            self.log_info(f"Collected {len(result.events)} events from Linear")

        except Exception as e:
            result.errors.append(f"Linear collection failed: {str(e)}")

        return result

    async def _graphql_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL request to Linear API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.API_URL,
                json={"query": query, "variables": variables or {}},
                headers={
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                raise Exception(f"GraphQL errors: {data['errors']}")

            return data.get("data", {})

    async def _get_viewer(self) -> Optional[Dict]:
        """Get current authenticated user."""
        query = """
        query {
            viewer {
                id
                name
                email
            }
        }
        """
        data = await self._graphql_request(query)
        return data.get("viewer")

    async def _get_issues_created_by(self) -> List[Dict]:
        """Get issues created by current user within date range."""
        query = """
        query($creatorId: ID!, $after: DateTime!, $before: DateTime!) {
            issues(
                filter: {
                    creator: { id: { eq: $creatorId } }
                    createdAt: { gte: $after, lte: $before }
                }
                first: 100
            ) {
                nodes {
                    id
                    identifier
                    title
                    description
                    url
                    createdAt
                    updatedAt
                    state { name }
                    assignee { id name }
                    creator { id name }
                    comments(first: 50) {
                        nodes {
                            id
                            body
                            createdAt
                            user { id name }
                        }
                    }
                }
            }
        }
        """
        data = await self._graphql_request(query, {
            "creatorId": self._viewer_id,
            "after": self.start_date.isoformat(),
            "before": self.end_date.isoformat(),
        })
        return data.get("issues", {}).get("nodes", [])

    async def _get_issues_assigned_to(self) -> List[Dict]:
        """Get issues assigned to current user with recent updates."""
        query = """
        query($assigneeId: ID!, $after: DateTime!, $before: DateTime!) {
            issues(
                filter: {
                    assignee: { id: { eq: $assigneeId } }
                    updatedAt: { gte: $after, lte: $before }
                }
                first: 100
            ) {
                nodes {
                    id
                    identifier
                    title
                    description
                    url
                    createdAt
                    updatedAt
                    state { name }
                    assignee { id name }
                    creator { id name }
                    comments(first: 50) {
                        nodes {
                            id
                            body
                            createdAt
                            user { id name }
                        }
                    }
                }
            }
        }
        """
        data = await self._graphql_request(query, {
            "assigneeId": self._viewer_id,
            "after": self.start_date.isoformat(),
            "before": self.end_date.isoformat(),
        })
        return data.get("issues", {}).get("nodes", [])

    async def _get_issues_commented_on(self) -> List[Dict]:
        """Get issues where user commented within date range."""
        # First get user's comments
        query = """
        query($userId: ID!, $after: DateTime!, $before: DateTime!) {
            comments(
                filter: {
                    user: { id: { eq: $userId } }
                    createdAt: { gte: $after, lte: $before }
                }
                first: 100
            ) {
                nodes {
                    id
                    issue {
                        id
                        identifier
                        title
                        description
                        url
                        createdAt
                        updatedAt
                        state { name }
                        assignee { id name }
                        creator { id name }
                        comments(first: 50) {
                            nodes {
                                id
                                body
                                createdAt
                                user { id name }
                            }
                        }
                    }
                }
            }
        }
        """
        data = await self._graphql_request(query, {
            "userId": self._viewer_id,
            "after": self.start_date.isoformat(),
            "before": self.end_date.isoformat(),
        })

        # Extract unique issues
        issues = []
        seen_ids = set()
        for comment in data.get("comments", {}).get("nodes", []):
            issue = comment.get("issue")
            if issue and issue.get("id") not in seen_ids:
                seen_ids.add(issue["id"])
                issues.append(issue)

        return issues

    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """Remove duplicate issues by ID."""
        seen = {}
        for issue in issues:
            issue_id = issue.get("id")
            if issue_id:
                seen[issue_id] = issue
        return list(seen.values())

    def _transform_issue(self, issue: Dict) -> List[ActivityEvent]:
        """Transform Linear issue to ActivityEvent(s)."""
        events = []

        # Event for issue creation if user is creator
        creator_id = issue.get("creator", {}).get("id")
        created_at = issue.get("createdAt", "")

        if creator_id == self._viewer_id and self.is_within_date_range(
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        ):
            events.append(self._create_issue_event(issue, EventType.ISSUE_CREATED, created_at))

        # Events for user's comments
        comments = issue.get("comments", {}).get("nodes", [])
        for comment in comments:
            comment_user_id = comment.get("user", {}).get("id")
            comment_created = comment.get("createdAt", "")

            if comment_user_id == self._viewer_id and comment_created:
                try:
                    comment_dt = datetime.fromisoformat(comment_created.replace("Z", "+00:00"))
                    if self.is_within_date_range(comment_dt):
                        events.append(self._create_comment_event(issue, comment))
                except ValueError:
                    pass

        # If user is assignee and issue was updated in range
        assignee_id = issue.get("assignee", {}).get("id")
        updated_at = issue.get("updatedAt", "")

        if (
            assignee_id == self._viewer_id
            and updated_at
            and not any(e.event_type == EventType.ISSUE_CREATED for e in events)
        ):
            try:
                updated_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                if self.is_within_date_range(updated_dt):
                    events.append(self._create_issue_event(issue, EventType.ISSUE_UPDATED, updated_at))
            except ValueError:
                pass

        return events

    def _create_issue_event(
        self,
        issue: Dict,
        event_type: EventType,
        timestamp: str
    ) -> ActivityEvent:
        """Create ActivityEvent from issue data."""
        identifier = issue.get("identifier", "")
        title = issue.get("title", "")
        description = issue.get("description", "") or ""
        url = issue.get("url", "")
        creator = issue.get("creator", {})

        # Determine ownership
        creator_id = creator.get("id")
        ownership = OwnershipType.MY_WORK if creator_id == self._viewer_id else OwnershipType.CONTEXT

        return ActivityEvent(
            event_id=self.generate_event_id("linear", issue.get("id", ""), timestamp),
            source_system=SourceSystem.LINEAR,
            event_type=event_type,
            event_timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
            title=f"[{identifier}] {title}",
            body_text=self.truncate_text(description),
            actor_name=creator.get("name", "Unknown"),
            ownership=ownership,
            confidence="high",
            source_pointers=[
                SourcePointer(
                    pointer_id=self.generate_pointer_id("linear_issue", url),
                    type="linear_issue_url",
                    url=url,
                    display_text=f"Linear {identifier}",
                )
            ],
            metadata={
                "identifier": identifier,
                "state": issue.get("state", {}).get("name", "Unknown"),
                "assignee": issue.get("assignee", {}).get("name"),
            },
        )

    def _create_comment_event(self, issue: Dict, comment: Dict) -> ActivityEvent:
        """Create ActivityEvent from comment data."""
        identifier = issue.get("identifier", "")
        issue_title = issue.get("title", "")
        comment_body = comment.get("body", "")
        comment_created = comment.get("createdAt", "")
        user = comment.get("user", {})
        issue_url = issue.get("url", "")
        comment_url = f"{issue_url}#comment-{comment.get('id', '')}"

        return ActivityEvent(
            event_id=self.generate_event_id("linear", comment.get("id", ""), comment_created),
            source_system=SourceSystem.LINEAR,
            event_type=EventType.COMMENT,
            event_timestamp=datetime.fromisoformat(comment_created.replace("Z", "+00:00")),
            title=f"Comment on [{identifier}] {issue_title}",
            body_text=self.truncate_text(comment_body),
            actor_name=user.get("name", "Unknown"),
            ownership=OwnershipType.MY_WORK,
            confidence="high",
            source_pointers=[
                SourcePointer(
                    pointer_id=self.generate_pointer_id("linear_comment", comment_url),
                    type="linear_comment_url",
                    url=comment_url,
                    display_text=f"Comment on {identifier}",
                )
            ],
            metadata={
                "issue_identifier": identifier,
                "comment_id": comment.get("id"),
            },
        )
