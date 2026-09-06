"""Connection management for Agorapulse Connector."""
from __future__ import annotations
import uuid
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import NoParams, ConnectParams, ConnectionIdParams, ConnectionRecord, ConnectionList, DeleteResult
from agorapulse_client import AgorapulseClient

async def resolve_client(ctx, connection_id: str = "") -> AgorapulseClient:
    connections = await ctx.store.get("connections", [])
    if not connections:
        raise ValueError("No Agorapulse connections configured. Use connect_agorapulse first.")
    conn = None
    if connection_id:
        for c in connections:
            if c.get("id") == connection_id:
                conn = c
                break
        if not conn:
            raise ValueError(f"Connection {connection_id} not found.")
    else:
        conn = connections[0]
    return AgorapulseClient(access_token=conn["access_token"], base_url=conn.get("base_url", ""))

@chat.function(
    "connect_agorapulse",
    "Connect Agorapulse account via OAuth 2.0 Access Token.",
    action_type="write",
    chain_callable=True,
    event="agorapulse-connector.connect_agorapulse",
    effects=["create:connection"],
    data_model=ConnectionRecord
)
async def connect_agorapulse(params: ConnectParams, ctx) -> ActionResult:
    client = AgorapulseClient(access_token=params.access_token, base_url=params.base_url)
    res = await client.verify_auth()
    if res.get("status") == "error":
        return ActionResult.error(f"Failed to authenticate with Agorapulse: {res.get('error')}")

    connections = await ctx.store.get("connections", [])
    masked = params.access_token[:6] + "..." if len(params.access_token) > 6 else "***"
    record = {
        "id": f"conn_{uuid.uuid4().hex[:8]}",
        "label": params.label or "Primary Agorapulse",
        "access_token": params.access_token,
        "masked_key": masked,
        "base_url": params.base_url,
        "is_active": True
    }
    connections.append(record)
    await ctx.store.set("connections", connections)
    return ActionResult.ok(ConnectionRecord(**{k: v for k, v in record.items() if k != "access_token"}), summary=f"Connected Agorapulse ({record['label']}) successfully.")

@chat.function(
    "list_connections",
    "List configured Agorapulse connections.",
    action_type="read",
    chain_callable=True,
    event="agorapulse-connector.list_connections",
    effects=["read:connections"],
    data_model=ConnectionList
)
async def list_connections(params: NoParams, ctx) -> ActionResult:
    conns = await ctx.store.get("connections", [])
    records = [ConnectionRecord(**{k: v for k, v in c.items() if k != "access_token"}) for c in conns]
    return ActionResult.ok(ConnectionList(connections=records, total=len(records)), summary=f"Found {len(records)} connection(s).")

@chat.function(
    "disconnect_agorapulse",
    "Disconnect Agorapulse account and remove saved credentials.",
    action_type="destructive",
    chain_callable=True,
    event="agorapulse-connector.disconnect_agorapulse",
    effects=["delete:connection"],
    data_model=DeleteResult
)
async def disconnect_agorapulse(params: ConnectionIdParams, ctx) -> ActionResult:
    conns = await ctx.store.get("connections", [])
    new_conns = [c for c in conns if c.get("id") != params.connection_id]
    if len(new_conns) == len(conns):
        return ActionResult.error(f"Connection {params.connection_id} not found.")
    await ctx.store.set("connections", new_conns)
    return ActionResult.ok(DeleteResult(success=True, message=f"Disconnected Agorapulse account {params.connection_id}."), summary="Disconnected connection successfully.")
