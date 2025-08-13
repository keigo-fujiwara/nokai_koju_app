# Render 環境変数設定手順

## 🔧 環境変数の設定手順

### 1. Renderダッシュボードでの設定

#### A. Webサービス（quiz-app）の環境変数設定

1. **Renderダッシュボード**にアクセス
2. **Services** → **quiz-app** をクリック
3. **Environment** タブをクリック
4. **Environment Variables** セクションで以下を設定：

**必須環境変数（既に設定済み）：**
- `DJANGO_SECRET_KEY` - Renderが自動生成済み
- `DATABASE_URL` - Renderが自動設定済み
- `DEBUG` - `false` に設定済み
- `ALLOWED_HOSTS` - `.onrender.com` に設定済み

**追加で設定が必要な環境変数：**

| キー | 値 | 説明 |
|------|-----|------|
| `EMAIL_HOST_USER` | あなたのGmailアドレス | 例: `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Gmailアプリパスワード | Gmailの2段階認証で生成 |
| `SITE_ID` | `1` | Django Sites framework用 |

#### B. Gmailアプリパスワードの取得方法

1. **Googleアカウント設定**にアクセス
2. **セキュリティ** → **2段階認証プロセス**を有効化
3. **アプリパスワード**を生成
4. **メール** → **Django** を選択
5. 生成された16文字のパスワードをコピー

### 2. 環境変数設定後の確認

#### A. 設定値の確認
```bash
# Renderのシェルで確認
echo $EMAIL_HOST_USER
echo $EMAIL_HOST_PASSWORD
echo $DATABASE_URL
```

#### B. アプリケーションの再起動
- 環境変数を設定後、**Manual Deploy** → **Deploy latest commit** を実行

### 3. よくある問題と解決方法

#### A. メール送信エラー
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```
**解決方法：**
- Gmailアプリパスワードが正しく設定されているか確認
- 2段階認証が有効になっているか確認

#### B. データベース接続エラー
```
connection to server failed
```
**解決方法：**
- `DATABASE_URL`が正しく設定されているか確認
- データベースサービスが起動しているか確認

### 4. 設定完了後のテスト

#### A. 管理者登録テスト
1. アプリケーションにアクセス
2. 管理者登録ページで新規登録
3. メール認証が正常に動作するか確認

#### B. クイズ機能テスト
1. 生徒アカウントでログイン
2. クイズを開始
3. 問題回答と結果表示を確認

### 5. トラブルシューティング

#### A. ログの確認方法
1. **Services** → **quiz-app** → **Logs** タブ
2. エラーメッセージを確認
3. 必要に応じて環境変数を修正

#### B. 再デプロイ方法
1. **Manual Deploy** → **Deploy latest commit**
2. ビルドログを確認
3. エラーがあれば修正して再実行

## 📞 サポート

問題が発生した場合は：
1. Renderのログを確認
2. 環境変数の設定を再確認
3. 必要に応じてサポートに問い合わせ
