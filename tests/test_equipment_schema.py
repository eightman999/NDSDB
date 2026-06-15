"""装備データのスキーマ準拠チェック (#2)。

`equipments_templates.yml` と実データの構造的な不変条件を検証する。
パース不能なファイル (マージコンフリクト等) は test_json_validity.py が
担当するため、ここではパース可能なファイルのみを対象にして「スキーマ」の
観点に集中する。
"""

from __future__ import annotations

import json
import numbers
from pathlib import Path

import pytest

from conftest import (
    REQUIRED_COMMON_KEYS,
    REQUIRED_TOP_LEVEL_KEYS,
    RESOURCE_KEYS,
    equipment_json_files,
    rel,
)


def _parseable_equipment() -> list[tuple[Path, dict]]:
    items = []
    for path in equipment_json_files():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # 不正な JSON は test_json_validity.py 側で検出する
            continue
        if isinstance(data, dict):
            items.append((path, data))
    return items


_EQUIPMENT = _parseable_equipment()
_IDS = [rel(p) for p, _ in _EQUIPMENT]


@pytest.mark.parametrize("data", [d for _, d in _EQUIPMENT], ids=_IDS)
def test_has_top_level_keys(data: dict):
    for key in REQUIRED_TOP_LEVEL_KEYS:
        assert key in data, f"トップレベルキー {key!r} がありません"


@pytest.mark.parametrize("data", [d for _, d in _EQUIPMENT], ids=_IDS)
def test_common_block_has_required_keys(data: dict):
    common = data.get("common")
    assert isinstance(common, dict), "common ブロックが辞書ではありません"
    missing = [k for k in REQUIRED_COMMON_KEYS if k not in common]
    assert not missing, f"common に不足キー: {missing}"


@pytest.mark.parametrize("data", [d for _, d in _EQUIPMENT], ids=_IDS)
def test_equipment_type_is_non_empty_string(data: dict):
    et = data.get("equipment_type")
    assert isinstance(et, str) and et.strip(), "equipment_type が空または文字列ではありません"


@pytest.mark.parametrize("data", [d for _, d in _EQUIPMENT], ids=_IDS)
def test_resources_are_non_negative_numbers(data: dict):
    common = data.get("common", {})
    for key in RESOURCE_KEYS:
        val = common.get(key)
        assert isinstance(val, numbers.Number) and not isinstance(val, bool), (
            f"{key} が数値ではありません: {val!r}"
        )
        assert val >= 0, f"{key} が負の値です: {val!r}"


@pytest.mark.parametrize(
    "path,data", _EQUIPMENT, ids=_IDS
)
def test_id_matches_directory_prefix(path: Path, data: dict):
    """ID は格納ディレクトリ名のプレフィックスを持つこと。

    例: equipments/SMAA/ 配下の ID は "SMAA" で始まる。
    """
    expected_prefix = path.parent.name
    equip_id = data.get("common", {}).get("ID")
    assert isinstance(equip_id, str) and equip_id, "ID が空または文字列ではありません"
    assert equip_id.startswith(expected_prefix), (
        f"ID {equip_id!r} がディレクトリのプレフィックス {expected_prefix!r} と一致しません"
    )


def test_ids_are_unique_within_equipments():
    """装備 ID は equipments/ 全体で一意であること。"""
    seen: dict[str, str] = {}
    dups: list[str] = []
    for path, data in _EQUIPMENT:
        equip_id = data.get("common", {}).get("ID")
        if not equip_id:
            continue
        if equip_id in seen:
            dups.append(f"{equip_id}: {seen[equip_id]} と {rel(path)}")
        else:
            seen[equip_id] = rel(path)
    assert not dups, "ID の重複:\n" + "\n".join(f"  - {d}" for d in dups)


def test_equipment_type_consistent_within_directory():
    """同一ディレクトリ内の装備は同じ equipment_type を持つこと。"""
    by_dir: dict[str, set[str]] = {}
    for path, data in _EQUIPMENT:
        et = data.get("equipment_type")
        by_dir.setdefault(path.parent.name, set()).add(et)
    inconsistent = {d: types for d, types in by_dir.items() if len(types) > 1}
    assert not inconsistent, f"ディレクトリ内で equipment_type が不一致: {inconsistent}"
