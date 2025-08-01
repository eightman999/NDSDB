
import yaml
import json
import os

def convert_smmg_yaml_to_json(template_path, example_json_path, smmg_files_dir):
    # テンプレートと例のJSONファイルを読み込む
    with open(template_path, 'r', encoding='utf-8') as f:
        templates = yaml.safe_load(f)

    with open(example_json_path, 'r', encoding='utf-8') as f:
        example_json = json.load(f)

    # SMMGのテンプレート情報を取得
    smmg_template = templates['gun_types']['medium_caliber_gun']

    # SMMGファイルを処理
    for i in range(1, 13): # SMMG001.ymlからSMMG012.ymlまで
        smmg_file_name = f"SMMG{i:03d}.yml"
        smmg_file_path = os.path.join(smmg_files_dir, smmg_file_name)
        
        if not os.path.exists(smmg_file_path):
            print(f"ファイルが見つかりません: {smmg_file_path}")
            continue

        with open(smmg_file_path, 'r', encoding='utf-8') as f:
            smmg_data = yaml.safe_load(f)

        # 新しいJSON構造を構築
        new_json_data = {
            "equipment_type": smmg_template['display_name'],
            "common": {},
            "specific": {},
            "stats": example_json['stats'] # SMLG_Mk7_5inch.jsonのstatsをそのままコピー
        }

        # common_elementsをマッピング
        new_json_data['common']['名前'] = smmg_data.get('name')
        new_json_data['common']['ID'] = smmg_data.get('id')
        new_json_data['common']['重量'] = smmg_data.get('weight')
        new_json_data['common']['人員'] = smmg_data.get('personnel')
        new_json_data['common']['開発年'] = smmg_data.get('developed_year')
        new_json_data['common']['開発国'] = smmg_data.get('country')
        
        resources = smmg_data.get('resources', {})
        new_json_data['common']['必要資源_鉄'] = resources.get('steel', 0)
        new_json_data['common']['必要資源_クロム'] = resources.get('chrome', 0)
        new_json_data['common']['必要資源_アルミ'] = resources.get('aluminum', 0)
        new_json_data['common']['必要資源_タングステン'] = resources.get('tungsten', 0)
        new_json_data['common']['必要資源_ゴム'] = resources.get('rubber', 0)

        # specific_elementsをマッピング
        specific_elements = smmg_data.get('specific_elements', {})
        new_json_data['specific']['shell_weight_kg'] = specific_elements.get('shell_weight_kg')
        new_json_data['specific']['initial_velocity_mps'] = specific_elements.get('initial_velocity_mps')
        new_json_data['specific']['rounds_per_minute'] = specific_elements.get('rounds_per_minute')
        new_json_data['specific']['caliber_cm'] = specific_elements.get('caliber_cm')
        new_json_data['specific']['barrel_length'] = specific_elements.get('barrel_length')
        new_json_data['specific']['barrel_count'] = specific_elements.get('barrel_count')
        new_json_data['specific']['max_elevation'] = specific_elements.get('max_elevation')
        new_json_data['specific']['turret_count'] = specific_elements.get('turret_count')

        # JSONファイルとして保存
        json_output_path = smmg_file_path.replace('.yml', '.json')
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(new_json_data, f, ensure_ascii=False, indent=2)
        print(f"変換完了: {smmg_file_path} -> {json_output_path}")

if __name__ == "__main__":
    base_dir = "/Users/eightman/Documents/NavalDesignSystem"
    template_file = os.path.join(base_dir, "equipments_templates.yml")
    example_json_file = os.path.join(base_dir, "equipments/SMLG/SMLG_Mk7_5inch.json")
    smmg_directory = os.path.join(base_dir, "equipments/SMMG")

    convert_smmg_yaml_to_json(template_file, example_json_file, smmg_directory)
