"""変換スクリプトのユニットテスト (#4)。

convert_smaa_to_json.py などは YAML を JSON に変換する。本番スクリプトは
base_dir をハードコードしているが、変換関数自体は (template, example, dir)
を引数に取るため、一時ディレクトリ上のフィクスチャで挙動を検証できる。
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from conftest import REPO_ROOT


def _load_module(filename: str):
    path = REPO_ROOT / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SMAA_TEMPLATE = {
    "gun_types": {
        "anti_aircraft_gun": {
            "display_name": "対空砲",
            "id_prefix": "SMAA",
        }
    }
}

EXAMPLE_JSON = {"stats": {"damage": 42, "range": 100}}

SMAA_YAML = {
    "name": "テスト対空砲",
    "id": "SMAA001",
    "weight": 3600.0,
    "personnel": 18,
    "developed_year": 1938,
    "country": "GER",
    "resources": {"steel": 10, "chrome": 5},  # aluminum 等は欠損 -> 0 になるはず
    "specific_elements": {
        "shell_weight_g": 120.0,
        "initial_velocity_mps": 875.0,
        "rounds_per_minute": 480,
        "caliber_mm": 2.0,
        "barrel_length": 65,
        "barrel_count": 2,
        "max_elevation": "+78/-10",
        "turret_count": 1,
    },
}


@pytest.fixture
def smaa_fixture(tmp_path: Path):
    template_path = tmp_path / "templates.yml"
    template_path.write_text(yaml.safe_dump(SMAA_TEMPLATE, allow_unicode=True), encoding="utf-8")

    example_path = tmp_path / "example.json"
    example_path.write_text(json.dumps(EXAMPLE_JSON, ensure_ascii=False), encoding="utf-8")

    smaa_dir = tmp_path / "SMAA"
    smaa_dir.mkdir()
    (smaa_dir / "SMAA001.yml").write_text(
        yaml.safe_dump(SMAA_YAML, allow_unicode=True), encoding="utf-8"
    )
    return template_path, example_path, smaa_dir


def test_smaa_conversion_produces_expected_mapping(smaa_fixture):
    template_path, example_path, smaa_dir = smaa_fixture
    mod = _load_module("convert_smaa_to_json.py")

    mod.convert_smaa_yaml_to_json(str(template_path), str(example_path), str(smaa_dir))

    out = smaa_dir / "SMAA001.json"
    assert out.exists(), "JSON が生成されていません"
    data = json.loads(out.read_text(encoding="utf-8"))

    # equipment_type はテンプレートの display_name
    assert data["equipment_type"] == "対空砲"
    # common ブロックのキー変換
    assert data["common"]["名前"] == "テスト対空砲"
    assert data["common"]["ID"] == "SMAA001"
    assert data["common"]["開発国"] == "GER"
    # 欠損リソースは 0 で埋められる
    assert data["common"]["必要資源_鉄"] == 10
    assert data["common"]["必要資源_アルミ"] == 0
    assert data["common"]["必要資源_ゴム"] == 0
    # specific ブロック
    assert data["specific"]["shell_weight_g"] == 120.0
    assert data["specific"]["barrel_count"] == 2
    # stats は example からそのままコピー
    assert data["stats"] == EXAMPLE_JSON["stats"]


def test_smaa_conversion_skips_missing_files(smaa_fixture, capsys):
    """存在しない連番ファイルはスキップされ、例外を投げないこと。"""
    template_path, example_path, smaa_dir = smaa_fixture
    mod = _load_module("convert_smaa_to_json.py")

    # SMAA001 のみ存在。残りの連番は見つからない旨を表示してスキップする。
    mod.convert_smaa_yaml_to_json(str(template_path), str(example_path), str(smaa_dir))
    captured = capsys.readouterr()
    assert "見つかりません" in captured.out
