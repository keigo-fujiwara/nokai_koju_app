import os
import requests
import json
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

print("=== 正しい別解データをSupabaseに反映 ===")

# 環境変数を取得
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

if not supabase_url or not supabase_key:
    print("❌ Supabase環境変数が設定されていません")
    exit(1)

# ヘッダーの設定
headers = {
    'apikey': supabase_key,
    'Authorization': f'Bearer {supabase_key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# エクセルで設定した正しい別解データ
# 問題IDと正解、別解のマッピング
correct_alternatives_data = {
    # 有機物関連
    719: {
        'correct_answer': '有機物',
        'alternatives': ['有機化合物', '有機物質']
    },
    720: {
        'correct_answer': '無機物',
        'alternatives': ['無機化合物', '無機物質']
    },
    721: {
        'correct_answer': 'プラスチック',
        'alternatives': ['合成樹脂', '合成高分子', '高分子化合物']
    },
    722: {
        'correct_answer': 'ポリエチレンテレフタラート',
        'alternatives': ['PET', 'ポリエステル']
    },
    
    # 金属関連
    723: {
        'correct_answer': '金属',
        'alternatives': ['金属元素', '金属材料']
    },
    724: {
        'correct_answer': '光沢',
        'alternatives': ['金属光沢', '輝き']
    },
    725: {
        'correct_answer': '電気伝導性',
        'alternatives': ['電気伝導体', '導電性']
    },
    726: {
        'correct_answer': '熱伝導性',
        'alternatives': ['熱伝導体', '熱伝導']
    },
    
    # 電気関連
    727: {
        'correct_answer': '電流',
        'alternatives': ['電気の流れ', '電流の流れ']
    },
    728: {
        'correct_answer': '電圧',
        'alternatives': ['電位差', '電圧差']
    },
    729: {
        'correct_answer': '抵抗',
        'alternatives': ['電気抵抗', '抵抗値']
    },
    730: {
        'correct_answer': 'オームの法則',
        'alternatives': ['オーム法則', '電流・電圧・抵抗の関係']
    },
    
    # 細胞関連
    731: {
        'correct_answer': '細胞核',
        'alternatives': ['核', '細胞の核']
    },
    732: {
        'correct_answer': '細胞質',
        'alternatives': ['原形質', '細胞の原形質']
    },
    733: {
        'correct_answer': '細胞膜',
        'alternatives': ['細胞の膜', '生体膜']
    },
    734: {
        'correct_answer': '葉緑体',
        'alternatives': ['葉緑素', '光合成器官']
    },
    735: {
        'correct_answer': 'ミトコンドリア',
        'alternatives': ['ミトコンドリア', '呼吸器官']
    },
    
    # 地学関連
    736: {
        'correct_answer': '地殻',
        'alternatives': ['地球の地殻', '岩石圏']
    },
    737: {
        'correct_answer': 'マントル',
        'alternatives': ['地球のマントル', '上部マントル']
    },
    738: {
        'correct_answer': '外核',
        'alternatives': ['地球の外核', '液体核']
    },
    739: {
        'correct_answer': '内核',
        'alternatives': ['地球の内核', '固体核']
    },
    740: {
        'correct_answer': 'プレート',
        'alternatives': ['プレートテクトニクス', '地殻プレート']
    },
    
    # 地理関連
    741: {
        'correct_answer': '都道府県',
        'alternatives': ['県', '府', '都']
    },
    742: {
        'correct_answer': '市区町村',
        'alternatives': ['市', '区', '町', '村']
    },
    743: {
        'correct_answer': '地方',
        'alternatives': ['地域', '地方区分']
    },
    744: {
        'correct_answer': '地域',
        'alternatives': ['地方', '地域区分']
    },
    745: {
        'correct_answer': '国',
        'alternatives': ['国家', '国名']
    },
    
    # 歴史関連
    746: {
        'correct_answer': '古代',
        'alternatives': ['古代史', '古代時代']
    },
    747: {
        'correct_answer': '中世',
        'alternatives': ['中世史', '中世時代']
    },
    748: {
        'correct_answer': '近世',
        'alternatives': ['近世史', '近世時代']
    },
    749: {
        'correct_answer': '近代',
        'alternatives': ['近代史', '近代時代']
    },
    750: {
        'correct_answer': '現代',
        'alternatives': ['現代史', '現代時代']
    }
}

print(f"📝 更新対象問題数: {len(correct_alternatives_data)}件")

# 1. まず現在のデータを確認
print("\n=== 現在のデータ確認 ===")
try:
    questions_url = f"{supabase_url}/rest/v1/quiz_app_question"
    response = requests.get(questions_url, headers=headers)
    
    if response.status_code == 200:
        questions_data = response.json()
        print(f"📊 総問題数: {len(questions_data)}件")
        
        # 更新対象の問題を確認
        for question_id, data in correct_alternatives_data.items():
            question = next((q for q in questions_data if q.get('id') == question_id), None)
            if question:
                current_alternatives = question.get('accepted_alternatives', [])
                print(f"問題ID {question_id}: 現在の別解 = {current_alternatives}")
            else:
                print(f"⚠️ 問題ID {question_id}: 見つかりません")
    else:
        print(f"❌ データ取得失敗: {response.status_code}")
        exit(1)
        
except Exception as e:
    print(f"❌ データ確認エラー: {e}")
    exit(1)

# 2. 正しい別解データを更新
print("\n=== 正しい別解データを更新中 ===")
updated_count = 0
failed_count = 0

for question_id, data in correct_alternatives_data.items():
    try:
        # PATCHリクエストで問題を更新
        update_url = f"{supabase_url}/rest/v1/quiz_app_question?id=eq.{question_id}"
        
        update_data = {
            'accepted_alternatives': data['alternatives']
        }
        
        response = requests.patch(update_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            updated_count += 1
            print(f'✅ 問題ID {question_id}: 別解を更新 ({", ".join(data["alternatives"])})')
        else:
            failed_count += 1
            print(f'❌ 問題ID {question_id}: 更新失敗 ({response.status_code})')
            print(f'レスポンス: {response.text}')
            
    except Exception as e:
        failed_count += 1
        print(f'❌ 問題ID {question_id} の更新エラー: {e}')

print(f'\n🎉 別解更新完了: {updated_count}件成功, {failed_count}件失敗')

# 3. 更新後の確認
print("\n=== 更新後の確認 ===")
try:
    questions_url = f"{supabase_url}/rest/v1/quiz_app_question"
    response = requests.get(questions_url, headers=headers)
    
    if response.status_code == 200:
        questions_data = response.json()
        
        # 別解がある問題をカウント
        questions_with_alternatives = [q for q in questions_data if q.get('accepted_alternatives') and len(q.get('accepted_alternatives', [])) > 0]
        print(f'📊 別解がある問題数: {len(questions_with_alternatives)} / {len(questions_data)}')
        
        # 更新した問題の例を表示
        print("\n=== 更新した問題の例 ===")
        for question_id, data in correct_alternatives_data.items():
            question = next((q for q in questions_data if q.get('id') == question_id), None)
            if question:
                alternatives = question.get('accepted_alternatives', [])
                print(f"\n--- 問題ID {question_id} ---")
                print(f"正解: {data['correct_answer']}")
                print(f"別解: {alternatives}")
                print(f"期待値: {data['alternatives']}")
                if alternatives == data['alternatives']:
                    print("✅ 正しく更新されています")
                else:
                    print("❌ 更新が正しく反映されていません")
            
    else:
        print(f'❌ 確認エラー: {response.status_code}')
        
except Exception as e:
    print(f'❌ 確認エラー: {e}')

print("\n=== 完了 ===")
