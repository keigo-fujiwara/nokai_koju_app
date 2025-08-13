# Render デプロイガイド

## 🚀 Render無料プランでのデプロイ手順

### 1. 事前準備

#### A. Renderアカウント作成
1. [Render.com](https://render.com) にアクセス
2. GitHubアカウントでサインアップ
3. 無料プランを選択

#### B. 必要な環境変数の準備
以下の環境変数をRenderで設定する必要があります：

**必須環境変数：**
- `DJANGO_SECRET_KEY` - Renderが自動生成
- `DATABASE_URL` - Renderが自動設定
- `DEBUG` - `false`に設定
- `ALLOWED_HOSTS` - `.onrender.com`に設定

**メール設定（オプション）：**
- `EMAIL_HOST_USER` - Gmailアドレス
- `EMAIL_HOST_PASSWORD` - Gmailアプリパスワード

### 2. デプロイ手順

#### A. GitHubリポジトリの準備
```bash
# 現在の変更をコミット
git add .
git commit -m "Render deployment preparation"
git push origin main
```

#### B. Renderでのサービス作成
1. Renderダッシュボードで「New +」をクリック
2. 「Blueprint」を選択
3. GitHubリポジトリを接続
4. `render.yaml`を自動検出
5. 環境変数を設定：
   - `EMAIL_HOST_USER`: あなたのGmailアドレス
   - `EMAIL_HOST_PASSWORD`: Gmailアプリパスワード

#### C. デプロイの実行
1. 「Create New Resources」をクリック
2. デプロイが自動開始
3. ビルドログを確認

### 3. デプロイ後の確認

#### A. アプリケーションの動作確認
1. 提供されたURLにアクセス
2. 管理者登録機能をテスト
3. クイズ機能をテスト

#### B. データベースの確認
```bash
# Renderのシェルで実行
python manage.py shell
>>> from quiz_app.models import Subject
>>> Subject.objects.count()
```

#### C. ログの確認
- Renderダッシュボードでログを確認
- エラーがあれば修正して再デプロイ

### 4. トラブルシューティング

#### A. よくある問題

**1. ビルドエラー**
```
Error: No module named 'psycopg2'
```
→ `requirements.txt`に`psycopg2-binary`が含まれているか確認

**2. データベース接続エラー**
```
Error: connection to server failed
```
→ `DATABASE_URL`が正しく設定されているか確認

**3. 静的ファイルエラー**
```
Error: Static files not found
```
→ `python manage.py collectstatic`が実行されているか確認

#### B. 解決方法

**1. 依存関係の問題**
```bash
# requirements.txtを更新
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

**2. 環境変数の問題**
- Renderダッシュボードで環境変数を再設定
- アプリケーションを再デプロイ

**3. データベースの問題**
```bash
# マイグレーションを再実行
python manage.py migrate
```

### 5. 本番環境での注意点

#### A. セキュリティ
- `DEBUG=False`を必ず設定
- 本番用の`SECRET_KEY`を使用
- HTTPSを有効化

#### B. パフォーマンス
- 静的ファイルの最適化
- データベースクエリの最適化
- キャッシュの活用

#### C. 監視
- ログの定期確認
- エラー通知の設定
- パフォーマンス監視

### 6. 無料プランの制限

#### A. リソース制限
- **CPU**: 0.1 CPU
- **RAM**: 512 MB
- **ストレージ**: 1 GB
- **月間使用時間**: 750時間

#### B. 制限への対応
- 軽量なアプリケーション設計
- 効率的なデータベースクエリ
- 静的ファイルの最適化

### 7. アップグレード時の注意

#### A. 有料プランへの移行
- データベースのバックアップ
- 環境変数の移行
- ドメインの設定

#### B. スケーリング
- 負荷分散の設定
- キャッシュの導入
- CDNの活用

## 📞 サポート

問題が発生した場合は：
1. Renderのドキュメントを確認
2. Djangoのログを確認
3. 必要に応じてサポートに問い合わせ
