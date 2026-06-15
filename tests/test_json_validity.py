"""データ妥当性ゲート (#1)。

リポジトリ内の全 JSON ファイルが構文的に正しいこと、および Git の
マージコンフリクトマーカーが混入していないことを検証する。これは最も
低コストで最も価値の高いテストであり、CI で常に実行されることを想定する。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import (
    REPO_ROOT,
    all_json_files,
    load_json_lenient,
    rel,
)

# Git のマージコンフリクトで残るマーカー
CONFLICT_MARKERS = ("<<<<<<<", "=======", ">>>>>>>")

_ALL_JSON = all_json_files()
# designs/ は本文前にディレクティブ行を持つ独自フォーマットのため別扱い
_DESIGNS = [p for p in _ALL_JSON if p.parts[len(REPO_ROOT.parts)] == "designs"]
_STRICT_JSON = [p for p in _ALL_JSON if p not in set(_DESIGNS)]


@pytest.mark.parametrize("path", _STRICT_JSON, ids=rel)
def test_json_parses(path: Path):
    """全ての JSON が json.load で読み込めること。"""
    with path.open(encoding="utf-8") as fh:
        json.load(fh)


@pytest.mark.parametrize("path", _DESIGNS, ids=rel)
def test_design_json_parses(path: Path):
    """designs/ の JSON は先頭ディレクティブ行を除去すれば読み込めること。"""
    load_json_lenient(path)


def _files_with_conflict_markers() -> list[str]:
    found = []
    for path in _ALL_JSON:
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if any(line.startswith(m) for m in CONFLICT_MARKERS):
                found.append(rel(path))
                break
    return found


def test_no_merge_conflict_markers():
    """コミット済みの JSON にマージコンフリクトマーカーが無いこと。"""
    offenders = _files_with_conflict_markers()
    assert not offenders, (
        f"{len(offenders)} 個のファイルにマージコンフリクトマーカーが残っています:\n"
        + "\n".join(f"  - {f}" for f in offenders[:50])
        + ("\n  ..." if len(offenders) > 50 else "")
    )


def test_json_files_exist():
    """テスト対象の JSON が実際に検出できていること (走査ロジックの保険)。"""
    assert len(_ALL_JSON) > 0
