"""HTTP client for Agorapulse API v1."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_BASE = "https://api.agorapulse.com/v1"

class AgorapulseClient:
    def __init__(self, access_token: str, base_url: str = ""):
        self.access_token = access_token.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Agorapulse-Connector/1.0.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def verify_auth(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/me", headers=self.headers)
                if resp.status_code in (200, 201):
                    return {"status": "ok", "data": resp.json()}
                return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    async def list_profiles(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/profiles", headers=self.headers)
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("profiles", data if isinstance(data, list) else [])

    async def list_posts(self, profile_id: str = "") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{self.base_url}/publishing/posts"
            params = {}
            if profile_id:
                params["profile_id"] = profile_id
            resp = await client.get(url, headers=self.headers, params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("posts", data if isinstance(data, list) else [])

    async def create_post(self, profile_id: str, text: str, scheduled_at: str = "") -> dict[str, Any]:
        payload = {"profile_id": profile_id, "text": text}
        if scheduled_at:
            payload["scheduled_at"] = scheduled_at
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/publishing/posts", headers=self.headers, json=payload)
            return resp.json() if resp.status_code in (200, 201) else {"error": resp.text, "status_code": resp.status_code}

    async def delete_post(self, post_id: str) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.delete(f"{self.base_url}/publishing/posts/{post_id}", headers=self.headers)
            return resp.status_code in (200, 204)

    async def list_inbox(self, profile_id: str = "") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{self.base_url}/inbox"
            params = {}
            if profile_id:
                params["profile_id"] = profile_id
            resp = await client.get(url, headers=self.headers, params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("items", data if isinstance(data, list) else [])
