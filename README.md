# 能開高受用科目アプリ

中学生向けの理科・社会クイズWebアプリケーションです。Django 5を使用して構築されており、生徒が楽しく学習できる環境を提供します。

## 機能

### 生徒向け機能
- 教科・単元選択によるクイズ
- 10問または20問のクイズモード
- リアルタイムタイマー（20秒制限）
- スペースキーでの開始、3秒カウントダウン
- 解答結果の詳細表示
- 間違い問題の再挑戦機能
- 学習記録の保存と分析
- 匿名ランキング表示

### 管理者向け機能
- XLSMファイルによる問題の一括登録
- 問題の個別編集・削除
- 利用状況分析（都道府県→学校→クラス→生徒）
- PDF自動生成（問題・解答付き）
- 宿題作成と公開管理

## 技術スタック

- **Backend**: Python 3.11 + Django 5
- **Frontend**: Django Template + Bootstrap 5 + HTMX + Alpine.js
- **Database**: PostgreSQL (Supabase)
- **Deployment**: Render
- **Authentication**: Django認証 + カスタムユーザーモデル

## セットアップ

### 開発環境

1. リポジトリをクローン
```bash
git clone <repository-url>
cd 能開高受用科目アプリ
```

2. 仮想環境を作成・有効化
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # macOS/Linux
```

3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

4. 環境変数を設定
```bash
# .envファイルを作成
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url  # 本番環境用
```

5. データベースマイグレーション
```bash
python manage.py migrate
```

6. 初期データを作成
```bash
python manage.py create_initial_data
```

7. 開発サーバーを起動
```bash
python manage.py runserver
```

### 本番環境（Render）

1. Renderアカウントを作成
2. 新しいWeb Serviceを作成
3. GitHubリポジトリを接続
4. 環境変数を設定：
   - `DJANGO_SECRET_KEY`
   - `DATABASE_URL` (Supabase接続文字列)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.onrender.com`

## データベース設計

### 主要モデル
- **User**: カスタムユーザーモデル（生徒/管理者）
- **StudentProfile**: 生徒プロファイル（学校、クラス等）
- **AdminProfile**: 管理者プロファイル
- **Subject**: 教科（理科/社会）
- **Unit**: 単元（中1化学、中2物理等）
- **Question**: 問題
- **QuizSession**: クイズセッション
- **QuizAttempt**: 解答記録
- **Homework**: 宿題

## XLSMファイル形式

アップロードするXLSMファイルは以下の列構成が必要です：

| 列 | 内容 | 例 |
|---|---|---|
| A | ID | 1, 2, 3... |
| B | 単元 | 中1化学, 中2物理... |
| C | 問題 | 問題文 |
| D | 解答 | 正解 |
| E | 別解 | 別解1/別解2 |

## 採点ロジック

- 基本的な文字列一致
- 別解の対応
- 複数解答欄（・区切り）の順不同対応
- 全角・半角、ひらがな・カタカナの正規化

## デプロイ

### Render
1. `render.yaml`ファイルが含まれているため、自動デプロイが可能
2. データベースは自動的に作成される
3. 環境変数はRenderダッシュボードで設定

### Supabase
1. Supabaseプロジェクトを作成
2. PostgreSQLデータベースの接続文字列を取得
3. `DATABASE_URL`環境変数に設定

## 開発者向け情報

### テストユーザー
- 管理者: `admin` / `admin123`
- 生徒: `student001` / `student123`

### 管理画面
- URL: `/admin/`
- Django標準の管理画面

### API
- REST API: `/api/`
- HTMXによる部分更新

## ライセンス

このプロジェクトは教育目的で作成されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。
