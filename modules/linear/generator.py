"""
Linear Ticket Generator

Ported from LINEAR_AUTO TypeScript implementation.
Batch ticket creation with dry-run mode and filters.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

try:
    import httpx
except ImportError:
    httpx = None

from .templates import (
    IssueTemplate,
    MatrixRow,
    DEFAULT_TEMPLATES,
    apply_template_variables,
)


@dataclass
class TicketRequest:
    """Request to create a ticket."""
    project_id: str
    project_name: str
    title: str
    description: str
    team_id: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    assignee_id: Optional[str] = None
    priority: Optional[int] = None


@dataclass
class TicketResult:
    """Result of ticket creation."""
    success: bool
    project_name: str
    issue_id: Optional[str] = None
    issue_url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class GeneratorConfig:
    """Configuration for ticket generator."""
    default_team_key: str
    default_labels: List[str] = field(default_factory=list)
    templates: Dict[str, IssueTemplate] = field(default_factory=dict)


class TicketGenerator:
    """
    Generates Linear tickets based on matrix data and templates.

    Features:
    - Dry-run mode for preview
    - Template variable substitution
    - Batch processing with filters
    - Team and label caching
    """

    API_URL = "https://api.linear.app/graphql"

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.api_key = os.getenv("LINEAR_API_KEY")
        self.team_cache: Dict[str, Dict[str, str]] = {}
        self.label_cache: Dict[str, List[str]] = {}

    async def initialize(self) -> bool:
        """Initialize generator and cache team data."""
        if not self.api_key:
            print("LINEAR_API_KEY not found")
            return False

        if httpx is None:
            print("httpx package required. Install with: pip install httpx")
            return False

        try:
            # Cache teams
            teams = await self._get_teams()
            for team in teams:
                key = team.get("key", "").lower()
                name = team.get("name", "").lower()
                team_id = team.get("id", "")

                self.team_cache[key] = {"id": team_id, "name": team.get("name", "")}
                self.team_cache[name] = {"id": team_id, "name": team.get("name", "")}

            print(f"TicketGenerator initialized. Found {len(teams)} teams.")
            return True

        except Exception as e:
            print(f"Failed to initialize: {e}")
            return False

    async def _graphql_request(
        self,
        query: str,
        variables: Optional[Dict] = None
    ) -> Dict[str, Any]:
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

    async def _get_teams(self) -> List[Dict]:
        """Get all teams."""
        query = """
        query {
            teams {
                nodes {
                    id
                    key
                    name
                }
            }
        }
        """
        data = await self._graphql_request(query)
        return data.get("teams", {}).get("nodes", [])

    async def _get_team_labels(self, team_id: str) -> List[Dict]:
        """Get labels for a team."""
        query = """
        query($teamId: String!) {
            team(id: $teamId) {
                labels {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """
        data = await self._graphql_request(query, {"teamId": team_id})
        return data.get("team", {}).get("labels", {}).get("nodes", [])

    def find_team(self, key_or_name: str) -> Optional[Dict[str, str]]:
        """Find team by key or name."""
        return self.team_cache.get(key_or_name.lower())

    async def find_labels(self, team_id: str, label_names: List[str]) -> List[str]:
        """Find label IDs for a team matching given names."""
        if team_id not in self.label_cache:
            labels = await self._get_team_labels(team_id)
            matching_ids = []
            for label in labels:
                label_name = label.get("name", "").lower()
                if any(name.lower() in label_name for name in label_names):
                    matching_ids.append(label.get("id"))
            self.label_cache[team_id] = matching_ids

        return self.label_cache.get(team_id, [])

    def apply_template(self, row: MatrixRow, template: IssueTemplate) -> TicketRequest:
        """Apply template to matrix row to create ticket request."""
        title = apply_template_variables(template.title_pattern, row)
        description = apply_template_variables(template.body_template, row)

        return TicketRequest(
            project_id=row.project_id,
            project_name=row.project_name,
            title=title,
            description=description,
            labels=template.labels.copy(),
            priority=template.priority,
        )

    async def create_ticket(
        self,
        request: TicketRequest,
        dry_run: bool = True
    ) -> TicketResult:
        """Create a single ticket in Linear."""
        team = self.find_team(self.config.default_team_key)
        if not team:
            return TicketResult(
                success=False,
                project_name=request.project_name,
                error=f"Team not found: {self.config.default_team_key}",
            )

        if dry_run:
            print("\n[DRY RUN] Would create ticket:")
            print(f"  Project: {request.project_name}")
            print(f"  Title: {request.title}")
            print(f"  Team: {team['name']}")
            print(f"  Labels: {', '.join(request.labels) if request.labels else 'none'}")
            print(f"  Body preview: {request.description[:100]}...")

            return TicketResult(
                success=True,
                project_name=request.project_name,
                issue_id="DRY_RUN",
                issue_url="https://linear.app/testbox/issue/DRY-RUN",
            )

        try:
            label_ids = await self.find_labels(team["id"], request.labels)

            mutation = """
            mutation($input: IssueCreateInput!) {
                issueCreate(input: $input) {
                    success
                    issue {
                        id
                        identifier
                        url
                    }
                }
            }
            """

            variables = {
                "input": {
                    "teamId": team["id"],
                    "title": request.title,
                    "description": request.description,
                    "projectId": request.project_id if request.project_id else None,
                    "labelIds": label_ids if label_ids else None,
                    "priority": request.priority,
                }
            }

            # Remove None values
            variables["input"] = {k: v for k, v in variables["input"].items() if v is not None}

            data = await self._graphql_request(mutation, variables)
            result = data.get("issueCreate", {})

            if result.get("success"):
                issue = result.get("issue", {})
                return TicketResult(
                    success=True,
                    project_name=request.project_name,
                    issue_id=issue.get("identifier"),
                    issue_url=issue.get("url"),
                )
            else:
                return TicketResult(
                    success=False,
                    project_name=request.project_name,
                    error="Issue creation failed",
                )

        except Exception as e:
            return TicketResult(
                success=False,
                project_name=request.project_name,
                error=str(e),
            )

    async def process_matrix(
        self,
        matrix: List[MatrixRow],
        template_id: str,
        filter_fn: Optional[Callable[[MatrixRow], bool]] = None,
        dry_run: bool = True,
    ) -> List[TicketResult]:
        """
        Process matrix with template and optional filter.

        Args:
            matrix: List of project matrix rows
            template_id: Template ID to use
            filter_fn: Optional filter function
            dry_run: If True, preview without creating (default: True)

        Returns:
            List of ticket results
        """
        # Get template
        template = self.config.templates.get(template_id)
        if not template:
            template = DEFAULT_TEMPLATES.get(template_id)

        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # Apply filter
        filtered = matrix
        if filter_fn:
            filtered = [row for row in matrix if filter_fn(row)]

        mode = "DRY RUN" if dry_run else "LIVE"
        print(f"\nProcessing {len(filtered)} projects with template: {template.name}")
        print(f"Mode: {mode}\n")

        results: List[TicketResult] = []

        for row in filtered:
            request = self.apply_template(row, template)
            result = await self.create_ticket(request, dry_run)
            results.append(result)

        return results

    async def create_at_risk_alerts(
        self,
        matrix: List[MatrixRow],
        dry_run: bool = True
    ) -> List[TicketResult]:
        """Create alerts for at-risk projects."""
        return await self.process_matrix(
            matrix,
            template_id="at_risk_alert",
            filter_fn=lambda row: row.health == "atRisk",
            dry_run=dry_run,
        )

    async def create_stale_reviews(
        self,
        matrix: List[MatrixRow],
        dry_run: bool = True
    ) -> List[TicketResult]:
        """Create reviews for stale projects."""
        return await self.process_matrix(
            matrix,
            template_id="stale_project",
            filter_fn=lambda row: (
                row.latest_update == "No updates" and
                row.current_state == "started"
            ),
            dry_run=dry_run,
        )

    async def create_milestone_tickets(
        self,
        matrix: List[MatrixRow],
        milestone_pct: int = 90,
        dry_run: bool = True
    ) -> List[TicketResult]:
        """Create celebration tickets for milestone achievements."""
        return await self.process_matrix(
            matrix,
            template_id="milestone_reached",
            filter_fn=lambda row: (
                row.progress_pct >= milestone_pct and
                row.health != "atRisk"
            ),
            dry_run=dry_run,
        )

    async def create_weekly_updates(
        self,
        matrix: List[MatrixRow],
        dry_run: bool = True
    ) -> List[TicketResult]:
        """Create weekly status update tickets for all active projects."""
        return await self.process_matrix(
            matrix,
            template_id="weekly_update",
            filter_fn=lambda row: row.current_state == "started",
            dry_run=dry_run,
        )


def create_generator(
    team_key: str = "RAC",
    default_labels: List[str] = None,
) -> TicketGenerator:
    """Factory function to create a ticket generator."""
    config = GeneratorConfig(
        default_team_key=team_key,
        default_labels=default_labels or ["auto-generated"],
        templates=DEFAULT_TEMPLATES.copy(),
    )
    return TicketGenerator(config)
