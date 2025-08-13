import os
import requests
import json
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

print("=== Supabaseの別解をクリアして更新 ===")

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

# 1. まずすべての問題の別解をクリア
print("🗑️ すべての問題の別解をクリア中...")

try:
    # すべての問題を取得
    questions_url = f"{supabase_url}/rest/v1/quiz_app_question"
    response = requests.get(questions_url, headers=headers)
    
    if response.status_code == 200:
        questions_data = response.json()
        print(f"📊 問題数: {len(questions_data)}件")
        
        # 各問題の別解を個別にクリア
        cleared_count = 0
        for question in questions_data:
            question_id = question.get('id')
            clear_url = f"{supabase_url}/rest/v1/quiz_app_question?id=eq.{question_id}"
            clear_data = {'accepted_alternatives': []}
            
            clear_response = requests.patch(clear_url, headers=headers, json=clear_data)
            if clear_response.status_code == 200:
                cleared_count += 1
            else:
                print(f"⚠️ 問題ID {question_id} のクリア失敗")
        
        print(f"✅ {cleared_count}件の問題の別解をクリアしました")
    else:
        print(f"❌ 問題取得失敗: {response.status_code}")
        exit(1)
        
except Exception as e:
    print(f"❌ 別解クリアエラー: {e}")
    exit(1)

# 2. 設定した別解データの定義
alternatives_data = {
    719: ['有機化合物'],  # 有機物
    720: ['無機化合物'],  # 無機物
    721: ['合成樹脂', '合成高分子'],  # プラスチック
    722: ['PET'],  # ポリエチレンテレフタラート
    723: ['金属元素'],  # 金属
    724: ['電気伝導体'],  # 導体
    725: ['電気絶縁体'],  # 絶縁体
    726: ['半導体'],  # 半導体
    727: ['電流'],  # 電流
    728: ['電圧'],  # 電圧
    729: ['細胞核'],  # 核
    730: ['細胞質'],  # 細胞質
    731: ['細胞膜'],  # 細胞膜
    732: ['葉緑体'],  # 葉緑体
    733: ['ミトコンドリア'],  # ミトコンドリア
    734: ['地殻'],  # 地殻
    735: ['マントル'],  # マントル
    736: ['外核'],  # 外核
    737: ['内核'],  # 内核
    738: ['プレート'],  # プレート
    739: ['都道府県'],  # 都道府県
    740: ['市区町村'],  # 市区町村
    741: ['地方'],  # 地方
    742: ['地域'],  # 地域
    743: ['国'],  # 国
    744: ['古代'],  # 古代
    745: ['中世'],  # 中世
    746: ['近世'],  # 近世
    747: ['近代'],  # 近代
    748: ['現代'],  # 現代
}

# 3. 設定した別解を追加
print("\n📝 設定した別解を追加中...")
updated_count = 0

for question_id, alternatives in alternatives_data.items():
    try:
        # PATCHリクエストで問題を更新
        update_url = f"{supabase_url}/rest/v1/quiz_app_question?id=eq.{question_id}"
        
        update_data = {
            'accepted_alternatives': alternatives
        }
        
        response = requests.patch(update_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            updated_count += 1
            print(f'✅ 問題ID {question_id}: 別解を設定 ({", ".join(alternatives)})')
        else:
            print(f'❌ 問題ID {question_id}: 更新失敗 ({response.status_code})')
            print(f'レスポンス: {response.text}')
            
    except Exception as e:
        print(f'❌ 問題ID {question_id} の更新エラー: {e}')

print(f'\n🎉 別解更新完了: {updated_count}件の問題を更新しました')

# 4. 更新後の確認
print("\n=== 更新後の確認 ===")
try:
    questions_url = f"{supabase_url}/rest/v1/quiz_app_question"
    response = requests.get(questions_url, headers=headers)
    
    if response.status_code == 200:
        questions_data = response.json()
        
        # 別解がある問題をカウント
        questions_with_alternatives = [q for q in questions_data if q.get('accepted_alternatives') and len(q.get('accepted_alternatives', [])) > 0]
        print(f'📊 別解がある問題数: {len(questions_with_alternatives)} / {len(questions_data)}')
        
        # 別解がある問題の例を表示
        if questions_with_alternatives:
            print("\n=== 別解がある問題の例 ===")
            for i, question in enumerate(questions_with_alternatives[:5], 1):
                print(f"\n--- 問題 {i} ---")
                print(f"ID: {question.get('id')}")
                print(f"正解: {question.get('correct_answer')}")
                print(f"別解: {question.get('accepted_alternatives')}")
        else:
            print("\n❌ 別解がある問題が見つかりませんでした")
            
    else:
        print(f'❌ 確認エラー: {response.status_code}')
        
except Exception as e:
    print(f'❌ 確認エラー: {e}')
