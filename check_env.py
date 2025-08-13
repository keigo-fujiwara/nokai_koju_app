import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

print("=== 環境変数確認 ===")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', '未設定')}")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY', '未設定')}")
print(f"SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY', '未設定')}")
print(f"SUPABASE_SERVICE_ROLE_KEY: {os.getenv('SUPABASE_SERVICE_ROLE_KEY', '未設定')}")

# 環境変数の存在確認
env_vars = {
    'SUPABASE_URL': os.getenv('SUPABASE_URL'),
    'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
    'SUPABASE_ANON_KEY': os.getenv('SUPABASE_ANON_KEY'),
    'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
}

print("\n=== 設定状況 ===")
for key, value in env_vars.items():
    status = "✅ 設定済み" if value else "❌ 未設定"
    print(f"{key}: {status}")

# Supabase接続テスト
if env_vars['SUPABASE_URL'] and env_vars['SUPABASE_ANON_KEY']:
    print("\n=== Supabase接続テスト ===")
    try:
        import requests
        
        url = f"{env_vars['SUPABASE_URL']}/rest/v1/quiz_app_subject"
        headers = {
            'apikey': env_vars['SUPABASE_ANON_KEY'],
            'Authorization': f'Bearer {env_vars["SUPABASE_ANON_KEY"]}'
        }
        
        response = requests.get(url, headers=headers)
        print(f"接続URL: {url}")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 接続成功: {len(data)}件のデータを取得")
        else:
            print(f"❌ 接続失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
else:
    print("\n❌ Supabase接続に必要な環境変数が設定されていません")
