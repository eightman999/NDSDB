# NDSDB

NDSDB は Naval Design System 向けのデータベースです。艦艇の設計情報や武装・センサーなどの装備データを JSON 形式で保存します。

## ディレクトリ
- `designs/` — 艦の設計定義
- `equipments/` — 装備品データを種類別に配置 (SMAA, SMLG など)
- `equipments_templates.yml` — 各装備タイプのフィールド構造を記したテンプレート
- `hulls_backup_*` — 船体データのバックアップ
- `fleets/` — 艦隊編成情報
- `convert_*.py` — YAML から JSON へ変換するスクリプト群

## スクリプトの実行例
変換スクリプトを動かすには Python3 と `pyyaml` が必要です。
```bash
pip install pyyaml
python convert_smaa_to_json.py  # anti_aircraft_gun 用
```
スクリプト内の `base_dir` を自身の環境に合わせて書き換えてから実行してください。

## ライセンス
本リポジトリのデータは研究目的で公開されています。商用利用を行う場合は作者へお問い合わせください。
