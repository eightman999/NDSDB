# テスト

NDSDB はデータ中心のリポジトリのため、テストは主に JSON/YAML データの
整合性を検証する。

## 実行方法

```bash
pip install -r requirements-dev.txt
pytest
```

## テストの構成

| ファイル | 目的 |
| --- | --- |
| `test_json_validity.py` | 全 JSON が構文的に正しく、マージコンフリクトマーカーが無いこと (#1) |
| `test_equipment_schema.py` | 装備データの構造・必須キー・ID 一意性・プレフィックス整合 (#2) |
| `test_converters.py` | `convert_*_to_json.py` の変換ロジックのユニットテスト (#4) |

## 既知の失敗 (要対応)

現在 `test_json_validity.py` は **79 個の JSON ファイル** で失敗する。これらは
未解決の Git マージコンフリクトマーカー (`<<<<<<<` / `=======` / `>>>>>>>`)
がコミットされたまま残っているためである (主に `equipments/SMLG`,
`equipments/SMMG`, `equipments/SMHG`)。

各コンフリクトは同一 ID に対して別々の装備を記述しており、どちらを採用すべきか
は機械的に判定できず、ドメイン知識に基づく手動解決が必要。テストはこの問題を
可視化するために意図的に失敗させている。解決後は自動的にグリーンになる。

## CI (手動追加が必要)

PR ごとにテストを走らせるには、以下を `.github/workflows/tests.yml` として
追加する (このファイルは `workflows` 権限の都合で自動コミットできないため、
リポジトリ管理者が手動で追加してください)。

```yaml
name: tests

on:
  push:
    branches: [master]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements-dev.txt
      - run: pytest -ra
```

## 今後のテスト拡張候補

- `designs/` と `fleets/` の参照整合性 (hull_id / 装備 ID の存在確認) (#3)
- `equipments_templates.yml` の型定義に対する厳密なスキーマ検証
- 変換スクリプトの共通化リファクタリングとそのテスト (#4)
