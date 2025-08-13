import os
import requests
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

print("=== Supabaseの別解データ確認 ===")

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

# 問題データの取得
questions_url = f"{supabase_url}/rest/v1/quiz_app_question"
print(f"📥 問題データ取得URL: {questions_url}")

try:
    response = requests.get(questions_url, headers=headers)
    print(f"📊 レスポンス: {response.status_code}")
    
    if response.status_code == 200:
        questions_data = response.json()
        print(f"❓ 問題データ: {len(questions_data)}件")
        
        # 別解がある問題を探す
        questions_with_alternatives = []
        for question in questions_data:
            alternatives = question.get('accepted_alternatives', [])
            if alternatives and len(alternatives) > 0:
                questions_with_alternatives.append(question)
        
        print(f"\n=== 別解がある問題数: {len(questions_with_alternatives)} / {len(questions_data)} ===")
        
        if questions_with_alternatives:
            print("\n=== 別解がある問題の例 ===")
            for i, question in enumerate(questions_with_alternatives[:3], 1):
                print(f"\n--- 別解あり問題 {i} ---")
                print(f"ID: {question.get('id')}")
                print(f"問題文: {question.get('text', '')[:100]}...")
                print(f"正解: {question.get('correct_answer')}")
                print(f"別解: {question.get('accepted_alternatives')}")
        else:
            print("\n❌ 別解がある問題が見つかりませんでした")
            
            # 最初の5問の詳細を表示
            print("\n=== 最初の5問の詳細 ===")
            for i, question in enumerate(questions_data[:5], 1):
                print(f"\n--- 問題 {i} ---")
                print(f"ID: {question.get('id')}")
                print(f"問題文: {question.get('text', '')[:100]}...")
                print(f"正解: {question.get('correct_answer')}")
                print(f"別解: {question.get('accepted_alternatives')}")
                print(f"選択肢: {question.get('choices')}")
                print(f"問題タイプ: {question.get('question_type')}")
        
    else:
        print(f"❌ エラー: {response.status_code}")
        print(f"レスポンス内容: {response.text}")
        
except Exception as e:
    print(f"❌ 接続エラー: {e}")
