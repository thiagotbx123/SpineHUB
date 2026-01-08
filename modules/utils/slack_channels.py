"""
Slack Channel Mapper - Discovery and member classification for Slack channels

Ported from GOD_EXTRACT Python implementation.
Discovers external channels and classifies members by role.
"""

import os
import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    WebClient = None
    SlackApiError = Exception


@dataclass
class ChannelInfo:
    """Information about a Slack channel."""
    id: str
    name: str
    is_private: bool = False
    num_members: int = 0


@dataclass
class MemberInfo:
    """Information about a Slack user."""
    id: str
    name: str
    real_name: str = ""
    display_name: str = ""
    email: str = ""
    is_bot: bool = False
    deleted: bool = False


@dataclass
class ChannelMapping:
    """Mapping of a channel with classified members."""
    channel: str
    channel_id: str
    tsa_members: List[str] = field(default_factory=list)
    eng_members: List[str] = field(default_factory=list)
    gtm_members: List[str] = field(default_factory=list)
    external_members: List[str] = field(default_factory=list)


class SlackChannelMapper:
    """
    Maps Slack channels and classifies members by role.

    Features:
    - Discovers channels by prefix (e.g., ext-, external-)
    - Fetches member lists with pagination
    - Classifies members into roles (TSA, ENG, GTM, External)
    """

    # Default role classification
    DEFAULT_TSA_MEMBERS = ["Thiago", "Diego", "Carlos", "Alexandra", "Gabrielle", "Katherine", "Thais", "Wakigawa"]
    DEFAULT_GTM_MEMBERS = ["Sam Senior", "James", "Rachel", "Meghan", "Josh", "Kat", "Shivani", "Gayathri"]
    DEFAULT_ENG_MEMBERS = ["Lucas Soranzo", "Gabriel Vieira", "Lucas Scheffel", "Leo", "Rafa", "Augusto"]

    def __init__(
        self,
        token: Optional[str] = None,
        company_domain: str = "@testbox.com",
        channel_prefixes: List[str] = None,
    ):
        """
        Initialize Slack channel mapper.

        Args:
            token: Slack User Token (xoxp-...) or Bot Token (xoxb-...)
            company_domain: Email domain for internal users
            channel_prefixes: Prefixes to filter channels (default: ["ext-", "external-"])
        """
        self.token = token or os.getenv("SLACK_USER_TOKEN") or os.getenv("SLACK_BOT_TOKEN")
        self.company_domain = company_domain
        self.channel_prefixes = channel_prefixes or ["ext-", "external-"]

        # Role classification lists (can be customized)
        self.tsa_members: Set[str] = set(self.DEFAULT_TSA_MEMBERS)
        self.gtm_members: Set[str] = set(self.DEFAULT_GTM_MEMBERS)
        self.eng_members: Set[str] = set(self.DEFAULT_ENG_MEMBERS)

        # User ID to name cache
        self.user_cache: Dict[str, str] = {}

        self._client: Optional[WebClient] = None

    def _get_client(self) -> WebClient:
        """Get or create Slack WebClient."""
        if self._client is None:
            if WebClient is None:
                raise ImportError("slack_sdk required. Install with: pip install slack-sdk")
            self._client = WebClient(token=self.token)
        return self._client

    def set_role_members(
        self,
        tsa: List[str] = None,
        gtm: List[str] = None,
        eng: List[str] = None,
    ) -> None:
        """
        Set custom role member lists.

        Args:
            tsa: TSA team member names
            gtm: GTM team member names
            eng: Engineering team member names
        """
        if tsa:
            self.tsa_members = set(tsa)
        if gtm:
            self.gtm_members = set(gtm)
        if eng:
            self.eng_members = set(eng)

    def add_user_mapping(self, user_id: str, name: str) -> None:
        """Add a user ID to name mapping."""
        self.user_cache[user_id] = name

    def get_user_role(self, name: str) -> str:
        """
        Determine user role based on name.

        Args:
            name: User's display name or real name

        Returns:
            Role string: "TSA", "ENG", "GTM", or "OTHER"
        """
        name_lower = name.lower()

        if any(tsa.lower() in name_lower for tsa in self.tsa_members):
            return "TSA"
        elif any(gtm.lower() in name_lower for gtm in self.gtm_members):
            return "GTM"
        elif any(eng.lower() in name_lower for eng in self.eng_members):
            return "ENG"

        return "OTHER"

    def list_channels(self, prefixes: List[str] = None) -> List[ChannelInfo]:
        """
        List channels matching prefixes.

        Args:
            prefixes: Channel name prefixes to filter

        Returns:
            List of matching channels
        """
        client = self._get_client()
        prefixes = prefixes or self.channel_prefixes
        channels = []
        cursor = None

        while True:
            try:
                response = client.conversations_list(
                    types="public_channel,private_channel",
                    limit=200,
                    cursor=cursor,
                )

                for channel in response.get("channels", []):
                    name = channel.get("name", "")
                    if any(name.startswith(prefix) for prefix in prefixes):
                        channels.append(ChannelInfo(
                            id=channel["id"],
                            name=name,
                            is_private=channel.get("is_private", False),
                            num_members=channel.get("num_members", 0),
                        ))

                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break

                time.sleep(0.5)  # Rate limiting

            except SlackApiError as e:
                print(f"Error listing channels: {e}")
                break

        return channels

    def get_channel_members(self, channel_id: str) -> List[str]:
        """
        Get member IDs for a channel.

        Args:
            channel_id: Slack channel ID

        Returns:
            List of member user IDs
        """
        client = self._get_client()
        members = []
        cursor = None

        while True:
            try:
                response = client.conversations_members(
                    channel=channel_id,
                    limit=200,
                    cursor=cursor,
                )

                members.extend(response.get("members", []))

                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break

                time.sleep(0.3)

            except SlackApiError as e:
                print(f"Error getting channel members: {e}")
                break

        return members

    def get_user_info(self, user_id: str) -> Optional[MemberInfo]:
        """
        Get user information by ID.

        Args:
            user_id: Slack user ID

        Returns:
            MemberInfo or None if not found
        """
        client = self._get_client()

        try:
            response = client.users_info(user=user_id)
            user = response.get("user", {})

            return MemberInfo(
                id=user_id,
                name=user.get("name", ""),
                real_name=user.get("real_name", ""),
                display_name=user.get("profile", {}).get("display_name", ""),
                email=user.get("profile", {}).get("email", ""),
                is_bot=user.get("is_bot", False),
                deleted=user.get("deleted", False),
            )

        except SlackApiError:
            return None

    def map_channel(self, channel: ChannelInfo) -> ChannelMapping:
        """
        Map a channel with classified members.

        Args:
            channel: Channel to map

        Returns:
            ChannelMapping with classified members
        """
        member_ids = self.get_channel_members(channel.id)

        tsa_list = []
        eng_list = []
        gtm_list = []
        external_list = []

        for member_id in member_ids:
            # Check cache first
            if member_id in self.user_cache:
                name = self.user_cache[member_id]
                role = self.get_user_role(name)

                if role == "TSA":
                    tsa_list.append(name)
                elif role == "ENG":
                    eng_list.append(name)
                elif role == "GTM":
                    gtm_list.append(name)
            else:
                # Fetch user info
                user_info = self.get_user_info(member_id)
                if user_info and not user_info.is_bot and not user_info.deleted:
                    email = user_info.email
                    name = user_info.real_name or user_info.display_name or user_info.name

                    if email and self.company_domain in email:
                        role = self.get_user_role(name)
                        if role == "TSA":
                            tsa_list.append(name)
                        elif role == "ENG":
                            eng_list.append(name)
                        elif role == "GTM":
                            gtm_list.append(name)
                    elif email:
                        external_list.append(name)

                    # Cache for future use
                    self.user_cache[member_id] = name

                time.sleep(0.2)  # Rate limiting

        return ChannelMapping(
            channel=channel.name,
            channel_id=channel.id,
            tsa_members=tsa_list,
            eng_members=eng_list,
            gtm_members=gtm_list,
            external_members=external_list[:5],  # Limit external to avoid noise
        )

    def map_all_channels(self, prefixes: List[str] = None) -> List[ChannelMapping]:
        """
        Map all channels matching prefixes.

        Args:
            prefixes: Channel prefixes to filter

        Returns:
            List of channel mappings
        """
        channels = self.list_channels(prefixes)
        print(f"Found {len(channels)} channels to map")

        mappings = []
        for i, channel in enumerate(channels):
            print(f"[{i+1}/{len(channels)}] Mapping {channel.name}...", end=" ")
            mapping = self.map_channel(channel)
            mappings.append(mapping)
            print(f"TSA:{len(mapping.tsa_members)} ENG:{len(mapping.eng_members)} GTM:{len(mapping.gtm_members)}")
            time.sleep(0.5)

        return mappings

    def export_to_json(self, mappings: List[ChannelMapping], filepath: str) -> None:
        """Export mappings to JSON file."""
        data = [
            {
                "channel": m.channel,
                "channel_id": m.channel_id,
                "tsa": m.tsa_members,
                "eng": m.eng_members,
                "gtm": m.gtm_members,
                "external": m.external_members,
            }
            for m in mappings
        ]

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Exported to {filepath}")
