"""共通フィクスチャとヘルパー。

データ中心のリポジトリのため、テストはファイルシステム上の JSON/YAML を
走査して検証する。ここではリポジトリのルート探索や、装備データの探索など、
複数のテストで共有するユーティリティを提供する。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

# リポジトリのルート (このファイルの 1 つ上のディレクトリ)
REPO_ROOT = Path(__file__).resolve().parent.parent

# 走査対象から除外するディレクトリ
EXCLUDED_DIR_PARTS = {".git", ".sync_backups", "__pycache__"}

# 装備データを格納するディレクトリ
EQUIPMENTS_DIR = REPO_ROOT / "equipments"

# 装備の「common」ブロックに必須のキー (全 845 件で一貫している)
REQUIRED_COMMON_KEYS = [
    "名前",
    "ID",
    "重量",
    "人員",
    "開発年",
    "開発国",
    "必要資源_鉄",
    "必要資源_クロム",
    "必要資源_アルミ",
    "必要資源_タングステン",
    "必要資源_ゴム",
]

# 装備 JSON のトップレベルに必須のキー
REQUIRED_TOP_LEVEL_KEYS = ["equipment_type", "common", "specific"]

# 必要資源フィールド (非負であることを検証する)
RESOURCE_KEYS = [
    "必要資源_鉄",
    "必要資源_クロム",
    "必要資源_アルミ",
    "必要資源_タングステン",
    "必要資源_ゴム",
]


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIR_PARTS for part in path.parts)


def iter_json_files(base: Path) -> list[Path]:
    """base 配下の全 .json ファイルを (除外ディレクトリを除いて) 返す。"""
    return [p for p in base.rglob("*.json") if not _is_excluded(p)]


def all_json_files() -> list[Path]:
    return iter_json_files(REPO_ROOT)


def equipment_json_files() -> list[Path]:
    if not EQUIPMENTS_DIR.is_dir():
        return []
    return iter_json_files(EQUIPMENTS_DIR)


def load_json_lenient(path: Path):
    """JSON を読み込む。先頭に `@directive` 行 (例: `@config.design`) が
    付いている場合はそれを除去してからパースする。

    一部のファイル (designs/ 配下など) は本文の前にディレクティブ行を持つ
    独自フォーマットになっているため、それを許容する。
    """
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("@"):
        # 先頭ディレクティブ行を取り除く
        _, _, rest = stripped.partition("\n")
        text = rest
    return json.loads(text)


def rel(path: Path) -> str:
    """テスト ID を見やすくするためのリポジトリ相対パス。"""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)
