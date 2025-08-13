#!/usr/bin/env python
"""
ローカル環境でSQLite3を使用するための環境設定スクリプト
"""
import os
import sys
import subprocess

def setup_local_environment():
    """ローカル環境をSQLite3用に設定"""
    print("🔧 ローカル環境をSQLite3用に設定中...")
    
    # 環境変数をクリア
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
        print("✅ DATABASE_URL環境変数をクリアしました")
    
    # DEBUGをTrueに設定
    os.environ['DEBUG'] = 'True'
    print("✅ DEBUG=Trueに設定しました")
    
    print("\n📋 現在の環境変数:")
    print(f"  - DEBUG: {os.getenv('DEBUG', '未設定')}")
    print(f"  - DATABASE_URL: {os.getenv('DATABASE_URL', '未設定')}")
    
    print("\n🎯 設定完了！")
    print("ローカル環境でSQLite3を使用します。")
    print("エクセルアップロードはSQLite3に保存されます。")

def test_database_connection():
    """データベース接続をテスト"""
    print("\n🔗 データベース接続テスト:")
    
    try:
        # Django設定を読み込み
        import django
        from pathlib import Path
        
        BASE_DIR = Path(__file__).resolve().parent
        sys.path.append(str(BASE_DIR))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        from django.conf import settings
        from django.db import connection
        
        db_config = settings.DATABASES['default']
        print(f"  - ENGINE: {db_config['ENGINE']}")
        print(f"  - NAME: {db_config['NAME']}")
        
        # 接続テスト
        with connection.cursor() as cursor:
            if 'sqlite' in db_config['ENGINE']:
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()
                print(f"  ✅ SQLite接続成功: {version[0]}")
            else:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"  ✅ PostgreSQL接続成功: {version[0]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ データベース接続エラー: {e}")
        return False

def main():
    print("🚀 ローカル環境設定スクリプト")
    print("=" * 50)
    
    # 環境設定
    setup_local_environment()
    
    # データベース接続テスト
    if test_database_connection():
        print("\n🎉 設定完了！ローカル環境でSQLite3を使用します。")
        print("\n📝 使用方法:")
        print("1. このスクリプトを実行してからDjangoサーバーを起動")
        print("2. エクセルアップロードはSQLite3に保存されます")
        print("3. 本番環境（Render）ではPostgreSQLを使用します")
    else:
        print("\n❌ 設定に問題があります。確認してください。")

if __name__ == '__main__':
    main()
