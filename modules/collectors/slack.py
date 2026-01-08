"""
Slack Message Collector

Collects messages from Slack using the Search API.
Ported from TSA_CORTEX TypeScript implementation.

Features:
- Ownership classification (my_work, mentioned, context)
- DM vs channel distinction
- Thread context support
- Pagination handling
- Rate limit awareness (20 req/s)

Requires:
- SLACK_USER_TOKEN (xoxp-) or SLACK_BOT_TOKEN (xoxb-)
- SLACK_USER_ID (for ownership classification)
"""

import os
import re
from datetime import datetime
from typing import Optional

from .base import (
    BaseCollector,
    CollectorResult,
    ActivityEvent,
    SourcePointer,
    SourceSystem,
    EventType,
    OwnershipType,
)

# Conditional import for slack_sdk
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    WebClient = None
    SlackApiError = Exception


class SlackCollector(BaseCollector):
    """
    Collector for Slack messages.

    Uses a three-pronged search approach:
    1. DMs: is:dm - Direct messages (my_work if sent, context if received)
    2. Channels: from:me -is:dm - Messages sent in channels (my_work)
    3. Mentions: <@userId> - Messages mentioning user (mentioned)

    Classification:
    - my_work: Messages authored by user (~45%)
    - mentioned: User was @mentioned (~5%)
    - context: Relevant but not owned (~50%)
    """

    MAX_PAGES = 10
    PAGE_SIZE = 100

    def __init__(
        self,
        config: dict,
        date_range: tuple[datetime, datetime],
        user_id: Optional[str] = None,
    ):
        super().__init__(config, date_range, user_id)

        # Get Slack credentials
        self.token = (
            config.get("SLACK_USER_TOKEN")
            or config.get("SLACK_BOT_TOKEN")
            or os.getenv("SLACK_USER_TOKEN")
            or os.getenv("SLACK_BOT_TOKEN")
        )
        self.slack_user_id = (
            config.get("SLACK_USER_ID")
            or os.getenv("SLACK_USER_ID")
            or user_id
        )

        self.client = None
        if self.token and SLACK_AVAILABLE:
            self.client = WebClient(token=self.token)

    @property
    def source(self) -> str:
        return SourceSystem.SLACK.value

    def is_configured(self) -> bool:
        """Check if Slack credentials are available."""
        if not SLACK_AVAILABLE:
            return False
        return bool(self.token and self.slack_user_id)

    async def collect(self) -> CollectorResult:
        """Collect Slack messages using search API."""
        result = self.create_empty_result()

        if not self.is_configured():
            if not SLACK_AVAILABLE:
                result.errors.append("slack_sdk not installed. Run: pip install slack-sdk")
            else:
                result.errors.append("Slack credentials not configured")
            return result

        # Format dates for Slack search
        date_after = self.start_date.strftime("%Y-%m-%d")
        date_before = self.end_date.strftime("%Y-%m-%d")

        all_events = []

        # Search 1: DMs
        self.log_info("Searching DMs...")
        dm_events = self._search_messages(
            query=f"is:dm after:{date_after} before:{date_before}",
            ownership_mode="dm",
            result=result,
        )
        all_events.extend(dm_events)

        # Search 2: Channel messages from me
        self.log_info("Searching channel messages...")
        channel_events = self._search_messages(
            query=f"from:me -is:dm after:{date_after} before:{date_before}",
            ownership_mode="my_work",
            result=result,
        )
        all_events.extend(channel_events)

        # Search 3: Mentions
        if self.slack_user_id:
            self.log_info("Searching mentions...")
            mention_events = self._search_messages(
                query=f"<@{self.slack_user_id}> -is:dm after:{date_after} before:{date_before}",
                ownership_mode="mentioned",
                result=result,
            )
            all_events.extend(mention_events)

        # Deduplicate by event_id
        seen_ids = set()
        unique_events = []
        for event in all_events:
            if event.event_id not in seen_ids:
                seen_ids.add(event.event_id)
                unique_events.append(event)

        result.events = unique_events

        # Statistics
        my_work = sum(1 for e in unique_events if e.ownership == OwnershipType.MY_WORK)
        mentioned = sum(1 for e in unique_events if e.ownership == OwnershipType.MENTIONED)
        context = sum(1 for e in unique_events if e.ownership == OwnershipType.CONTEXT)

        self.log_info(
            f"Collected {len(unique_events)} messages: "
            f"my_work={my_work}, mentioned={mentioned}, context={context}"
        )

        return result

    def _search_messages(
        self,
        query: str,
        ownership_mode: str,
        result: CollectorResult,
    ) -> list[ActivityEvent]:
        """Execute a Slack search and return events."""
        events = []
        page = 1

        while page <= self.MAX_PAGES:
            try:
                response = self.client.search_messages(
                    query=query,
                    count=self.PAGE_SIZE,
                    page=page,
                    sort="timestamp",
                    sort_dir="desc",
                )

                messages = response.get("messages", {}).get("matches", [])

                for msg in messages:
                    event = self._parse_message(msg, ownership_mode)
                    if event:
                        events.append(event)

                # Check if more pages
                if len(messages) < self.PAGE_SIZE:
                    break

                page += 1

            except SlackApiError as e:
                error_msg = f"Slack API error: {e.response.get('error', str(e))}"
                result.errors.append(error_msg)
                self.log_error(error_msg)
                break
            except Exception as e:
                result.errors.append(f"Search error: {str(e)}")
                self.log_error(str(e))
                break

        return events

    def _parse_message(self, msg: dict, ownership_mode: str) -> Optional[ActivityEvent]:
        """Parse a Slack message into an ActivityEvent."""
        # Extract timestamp
        ts = msg.get("ts")
        if not ts:
            return None

        try:
            timestamp = datetime.fromtimestamp(float(ts))
        except (ValueError, TypeError):
            return None

        if not self.is_within_date_range(timestamp):
            return None

        # Extract text
        text = msg.get("text", "")
        if not text:
            return None

        # Determine ownership
        user = msg.get("user") or msg.get("username", "")
        channel = msg.get("channel", {})
        channel_id = channel.get("id") if isinstance(channel, dict) else channel
        channel_name = channel.get("name", "") if isinstance(channel, dict) else ""

        if ownership_mode == "dm":
            # In DMs, classify based on who sent it
            if user == self.slack_user_id:
                ownership = OwnershipType.MY_WORK
            else:
                ownership = OwnershipType.CONTEXT
        elif ownership_mode == "my_work":
            ownership = OwnershipType.MY_WORK
        elif ownership_mode == "mentioned":
            ownership = OwnershipType.MENTIONED
        else:
            ownership = OwnershipType.CONTEXT

        # Generate event ID
        event_id = self.generate_event_id(self.source, channel_id, ts)

        # Create title from text
        title = self._create_title(text)
        body = self.truncate_text(text, 500)

        # Build permalink
        permalink = msg.get("permalink", "")
        if not permalink and channel_id:
            permalink = f"https://slack.com/archives/{channel_id}/p{ts.replace('.', '')}"

        pointer = SourcePointer(
            pointer_id=self.generate_pointer_id("slack_msg", permalink or ts),
            type="slack_message_permalink",
            url=permalink,
            display_text=f"Slack message in #{channel_name or 'dm'}",
        )

        # Extract mentioned users
        mentions = re.findall(r"<@([A-Z0-9]+)>", text)

        return ActivityEvent(
            event_id=event_id,
            source_system=SourceSystem.SLACK,
            event_type=EventType.MESSAGE,
            event_timestamp=timestamp,
            title=title,
            body_text=body,
            actor_name=self._get_user_name(user),
            ownership=ownership,
            confidence="high" if ownership == OwnershipType.MY_WORK else "medium",
            source_pointers=[pointer],
            metadata={
                "channel_id": channel_id,
                "channel_name": channel_name,
                "user_id": user,
                "thread_ts": msg.get("thread_ts"),
                "mentions": mentions,
                "is_dm": ownership_mode == "dm",
            },
        )

    def _create_title(self, text: str) -> str:
        """Create a title from message text."""
        # Remove Slack formatting
        clean = re.sub(r"<@[A-Z0-9]+>", "", text)  # Remove mentions
        clean = re.sub(r"<#[A-Z0-9]+\|([^>]+)>", r"#\1", clean)  # Channel refs
        clean = re.sub(r"<([^|>]+)\|([^>]+)>", r"\2", clean)  # Links
        clean = re.sub(r"<([^>]+)>", r"\1", clean)  # Remaining links
        clean = re.sub(r"\s+", " ", clean).strip()  # Collapse whitespace

        # Truncate
        if len(clean) > 120:
            truncated = clean[:120]
            last_space = truncated.rfind(" ")
            if last_space > 80:
                truncated = truncated[:last_space]
            clean = truncated + "..."

        return clean or "Slack message"

    def _get_user_name(self, user_id: str) -> str:
        """Get display name for a user ID."""
        # Simple implementation - could be enhanced with API lookup
        if user_id == self.slack_user_id:
            return "Me"
        return user_id
