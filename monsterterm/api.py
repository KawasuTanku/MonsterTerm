"""Monster API client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class MonsterConfig:
    base_url: str
    token: str

    @classmethod
    def from_env(cls) -> MonsterConfig:
        base_url = os.getenv("MONSTER_URL", "https://monster.warpstrand.com")
        token = os.getenv("MONSTER_TOKEN", "")
        return cls(base_url=base_url, token=token)

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "User-Agent": "MonsterTerm/0.1.0"}


def get_json(url: str, token: str) -> dict[str, Any] | None:
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def fetch_stats(cfg: MonsterConfig) -> dict[str, Any] | None:
    return get_json(f"{cfg.base_url}/api/stats", cfg.token)


def fetch_inventory(cfg: MonsterConfig) -> list[dict] | None:
    data = get_json(f"{cfg.base_url}/api/inventory", cfg.token)
    if data and "items" in data:
        return data["items"]
    return None


def fetch_inventory_low(cfg: MonsterConfig) -> list[dict] | None:
    data = get_json(f"{cfg.base_url}/api/inventory/low", cfg.token)
    if data and "items" in data:
        return data["items"]
    return None


def fetch_summary(cfg: MonsterConfig) -> dict[str, Any] | None:
    return get_json(f"{cfg.base_url}/api/report/summary", cfg.token)


def fetch_monthly(cfg: MonsterConfig) -> list[dict] | None:
    data = get_json(f"{cfg.base_url}/api/report/monthly", cfg.token)
    if data and "months" in data:
        return data["months"]
    return None


def fetch_item(cfg: MonsterConfig, item_id: str) -> dict[str, Any] | None:
    return get_json(f"{cfg.base_url}/api/inventory/{item_id}", cfg.token)
