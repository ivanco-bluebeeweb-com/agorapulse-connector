"""Resource handlers for Agorapulse Connector."""
from __future__ import annotations
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from handlers_connection import resolve_client
from schemas import (
    ListProfilesParams, ProfileList, ProfileRecord,
    PublishPostParams, PostRecord, ListPostsParams, PostList, DeletePostParams,
    ListInboxParams, InboxList, InboxItem, HealthAuditResult, DeleteResult, ConnectionIdParams
)

@chat.function(
    "list_profiles",
    "List social media profiles managed in Agorapulse.",
    action_type="read",
    chain_callable=True,
    event="agorapulse-connector.list_profiles",
    effects=["read:profiles"],
    data_model=ProfileList
)
async def list_profiles(ctx, params: ListProfilesParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    items = await client.list_profiles()
    records = [
        ProfileRecord(
            id=str(p.get("id", "")),
            name=str(p.get("name", "Unknown")),
            platform=str(p.get("type", p.get("platform", "generic"))),
            status=str(p.get("status", "active")),
            raw=p
        ) for p in items
    ]
    return ActionResult.ok(ProfileList(profiles=records, total=len(records)), summary=f"Loaded {len(records)} profiles.")

@chat.function(
    "list_posts",
    "List scheduled or published posts in Agorapulse.",
    action_type="read",
    chain_callable=True,
    event="agorapulse-connector.list_posts",
    effects=["read:posts"],
    data_model=PostList
)
async def list_posts(ctx, params: ListPostsParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    items = await client.list_posts(profile_id=params.profile_id or "")
    records = [
        PostRecord(
            id=str(p.get("id", "")),
            profile_id=str(p.get("profile_id", "")),
            text=str(p.get("text", "")),
            status=str(p.get("status", "published")),
            scheduled_at=p.get("scheduled_at"),
            raw=p
        ) for p in items
    ]
    return ActionResult.ok(PostList(posts=records, total=len(records)), summary=f"Found {len(records)} posts.")

@chat.function(
    "create_post",
    "Publish or schedule a social media post in Agorapulse.",
    action_type="write",
    chain_callable=True,
    event="agorapulse-connector.create_post",
    effects=["create:post"],
    data_model=PostRecord
)
async def create_post(ctx, params: PublishPostParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    res = await client.create_post(profile_id=params.profile_id, text=params.text, scheduled_at=params.scheduled_at or "")
    if "error" in res:
        return ActionResult.error(f"Failed to publish post: {res['error']}")
    rec = PostRecord(
        id=str(res.get("id", "post_draft")),
        profile_id=params.profile_id,
        text=params.text,
        status="scheduled" if params.scheduled_at else "published",
        scheduled_at=params.scheduled_at,
        raw=res
    )
    return ActionResult.ok(rec, summary=f"Created post {rec.id} for profile {params.profile_id}.")

@chat.function(
    "delete_post",
    "Delete a post from Agorapulse calendar.",
    action_type="destructive",
    chain_callable=True,
    event="agorapulse-connector.delete_post",
    effects=["delete:post"],
    data_model=DeleteResult
)
async def delete_post(ctx, params: DeletePostParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    ok = await client.delete_post(post_id=params.post_id)
    if not ok:
        return ActionResult.error(f"Could not delete post {params.post_id}.")
    return ActionResult.ok(DeleteResult(success=True, message=f"Deleted post {params.post_id}."), summary="Deleted post successfully.")

@chat.function(
    "list_inbox",
    "List social inbox conversations and comments.",
    action_type="read",
    chain_callable=True,
    event="agorapulse-connector.list_inbox",
    effects=["read:inbox"],
    data_model=InboxList
)
async def list_inbox(ctx, params: ListInboxParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    items = await client.list_inbox(profile_id=params.profile_id or "")
    records = [
        InboxItem(
            id=str(i.get("id", "")),
            profile_id=str(i.get("profile_id", "")),
            author=str(i.get("author", "Anonymous")),
            content=str(i.get("content", "")),
            item_type=str(i.get("type", "comment")),
            created_at=i.get("created_at")
        ) for i in items
    ]
    return ActionResult.ok(InboxList(items=records, total=len(records)), summary=f"Found {len(records)} inbox items.")

@chat.function(
    "audit_social_health",
    "Audit Agorapulse profiles and social inbox health.",
    action_type="read",
    chain_callable=True,
    event="agorapulse-connector.audit_social_health",
    effects=["read:health"],
    data_model=HealthAuditResult
)
async def audit_social_health(ctx, params: ConnectionIdParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    profiles = await client.list_profiles()
    posts = await client.list_posts()
    inbox = await client.list_inbox()
    result = HealthAuditResult(
        total_profiles=len(profiles),
        scheduled_posts=len(posts),
        unread_inbox_items=len(inbox),
        status="healthy" if len(profiles) > 0 else "no_profiles_connected"
    )
    return ActionResult.ok(result, summary=f"Agorapulse health audit: {len(profiles)} profiles, {len(posts)} posts, {len(inbox)} inbox items.")
