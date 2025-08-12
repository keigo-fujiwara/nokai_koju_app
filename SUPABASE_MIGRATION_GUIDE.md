# Supabase移行ガイド

このガイドでは、現在のSQLiteデータベースからSupabase（PostgreSQL）への移行手順を説明します。

## 前提条件

1. Supabaseアカウント（無料プラン）
2. Python 3.8以上
3. 現在のDjangoプロジェクトが正常に動作していること

## 手順

### 1. Supabaseプロジェクトの作成

1. [Supabase](https://supabase.com)にアクセスしてアカウントを作成
2. 新しいプロジェクトを作成
3. プロジェクト設定から以下の情報を取得：
   - Project URL
   - Anon Key
   - Service Role Key
   - Database Password

### 2. 環境変数の設定

1. `.env`ファイルを作成（`env.example`をコピー）
2. 以下の値を設定：

```env
# Supabase設定
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# データベースURL
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. Supabaseデータベースの準備

1. SupabaseダッシュボードでSQLエディタを開く
2. 以下のSQLを実行してテーブルを作成：

```sql
-- ユーザーテーブル
CREATE TABLE accounts_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    grade_year VARCHAR(10),
    school_name VARCHAR(100)
);

-- 教科テーブル
CREATE TABLE quiz_app_subject (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    label_ja VARCHAR(20) NOT NULL
);

-- 単元テーブル
CREATE TABLE quiz_app_unit (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES quiz_app_subject(id),
    grade_year VARCHAR(10) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_key VARCHAR(100) UNIQUE NOT NULL
);

-- 問題テーブル
CREATE TABLE quiz_app_question (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL REFERENCES quiz_app_unit(id),
    source_id VARCHAR(50) NOT NULL,
    question_type VARCHAR(10) NOT NULL,
    text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    accepted_alternatives JSONB NOT NULL,
    choices JSONB NOT NULL,
    requires_unit_label BOOLEAN NOT NULL,
    unit_label_text VARCHAR(50),
    explanation TEXT,
    difficulty_level INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- クイズセッションテーブル
CREATE TABLE quiz_app_quizsession (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id),
    unit_id INTEGER NOT NULL REFERENCES quiz_app_unit(id),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    question_ids JSONB NOT NULL,
    choice_mappings JSONB NOT NULL
);

-- クイズ結果テーブル
CREATE TABLE quiz_app_quizresult (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES quiz_app_quizsession(id),
    question_id INTEGER NOT NULL REFERENCES quiz_app_question(id),
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    score INTEGER NOT NULL,
    time_taken INTEGER,
    answered_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### 5. データベース設定の変更

`config/settings.py`でデータベース設定を確認：

```python
# 環境変数DATABASE_URLが設定されている場合、Supabaseを使用
if os.getenv('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
    }
```

### 6. マイグレーションの実行

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. データ移行の実行

```bash
python migrate_to_supabase.py
```

### 8. 接続テストの実行

```bash
python test_supabase_connection.py
```

## トラブルシューティング

### よくある問題

1. **接続エラー**
   - 環境変数が正しく設定されているか確認
   - Supabaseプロジェクトの設定を確認

2. **テーブルが見つからない**
   - SQLエディタでテーブルが正しく作成されているか確認
   - テーブル名の大文字小文字を確認

3. **権限エラー**
   - Service Role Keyを使用しているか確認
   - RLS（Row Level Security）の設定を確認

### ロールバック手順

問題が発生した場合、SQLiteに戻す：

1. `.env`ファイルから`DATABASE_URL`を削除
2. `python manage.py migrate`を実行してSQLiteに戻す

## 注意事項

- 本番環境での移行前に必ずテスト環境でテストしてください
- データ移行前にバックアップを取得してください
- Supabaseの無料プランには制限があります（500MB、2プロジェクトなど）

## 次のステップ

移行が完了したら：

1. アプリケーションの動作確認
2. パフォーマンステスト
3. バックアップ戦略の検討
4. 監視とログの設定
