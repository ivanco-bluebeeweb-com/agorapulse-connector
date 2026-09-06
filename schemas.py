"""Pydantic schemas for Agorapulse Connector (C31. Social Media Management)."""
from __future__ import annotations
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    """Empty parameters model."""
    pass

class ConnectParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label, e.g. Primary Agorapulse.")
    access_token: str = Field(description="Agorapulse OAuth 2.0 Access Token.")
    base_url: str = Field(default="https://api.agorapulse.com/v1", description="Agorapulse API base URL.")

class ConnectionIdParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier (empty uses active connection).")

class ConnectionRecord(BaseModel):
    id: str
    label: str
    masked_key: str
    base_url: str
    is_active: bool

class ConnectionList(BaseModel):
    connections: list[ConnectionRecord]
    total: int

class DeleteResult(BaseModel):
    success: bool
    message: str

class ProfileRecord(BaseModel):
    id: str
    name: str
    platform: str
    status: str
    raw: Dict[str, Any] = Field(default_factory=dict)

class ProfileList(BaseModel):
    profiles: list[ProfileRecord]
    total: int

class ListProfilesParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")

class PublishPostParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    profile_id: str = Field(description="Target Agorapulse social profile ID.")
    text: str = Field(description="Message body text.")
    scheduled_at: Optional[str] = Field(default=None, description="ISO 8601 publication datetime.")

class PostRecord(BaseModel):
    id: str
    profile_id: str
    text: str
    status: str
    scheduled_at: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

class ListPostsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    profile_id: Optional[str] = Field(default=None, description="Filter by profile ID.")

class PostList(BaseModel):
    posts: list[PostRecord]
    total: int

class DeletePostParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    post_id: str = Field(description="Post ID to delete.")

class InboxItem(BaseModel):
    id: str
    profile_id: str
    author: str
    content: str
    item_type: str
    created_at: Optional[str] = None

class InboxList(BaseModel):
    items: list[InboxItem]
    total: int

class ListInboxParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    profile_id: Optional[str] = Field(default=None, description="Filter by profile ID.")

class HealthAuditResult(BaseModel):
    total_profiles: int
    scheduled_posts: int
    unread_inbox_items: int
    status: str
