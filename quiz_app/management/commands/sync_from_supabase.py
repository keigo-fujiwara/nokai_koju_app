import os
import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from quiz_app.models import Question


class Command(BaseCommand):
    help = 'Supabaseからaccepted_alternativesデータを同期します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subject',
            type=str,
            help='特定の教科コードを指定（例: science）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='実際の更新を行わず、変更内容のみを表示',
        )

    def handle(self, *args, **options):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            self.stdout.write(
                self.style.ERROR('Supabase環境変数が設定されていません。')
            )
            return
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
        }
        
        # 対象の質問を取得
        questions = Question.objects.all()
        if options['subject']:
            questions = questions.filter(unit__subject__code=options['subject'])
        
        self.stdout.write(f'対象問題数: {questions.count()}')
        
        updated_count = 0
        failed_count = 0
        errors = []
        
        for question in questions:
            try:
                # Supabaseからデータを取得
                response = requests.get(
                    f"{supabase_url}/rest/v1/quiz_app_question?id=eq.{question.id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code != 200:
                    failed_count += 1
                    error_msg = f"問題ID {question.id} 取得失敗 ({response.status_code})"
                    errors.append(error_msg)
                    continue
                
                data = response.json()
                if not data:
                    failed_count += 1
                    error_msg = f"問題ID {question.id} データが見つかりません"
                    errors.append(error_msg)
                    continue
                
                supabase_alternatives = data[0].get('accepted_alternatives', [])
                
                # 現在のDjangoデータと比較
                current_alternatives = question.accepted_alternatives or []
                
                if isinstance(current_alternatives, str):
                    try:
                        current_alternatives = json.loads(current_alternatives)
                    except json.JSONDecodeError:
                        current_alternatives = []
                
                if not isinstance(current_alternatives, list):
                    current_alternatives = []
                
                # データが異なる場合
                if current_alternatives != supabase_alternatives:
                    if options['dry_run']:
                        self.stdout.write(
                            f"問題ID {question.id}: 更新予定\n"
                            f"  現在: {current_alternatives}\n"
                            f"  Supabase: {supabase_alternatives}"
                        )
                    else:
                        # Djangoデータを更新
                        question.accepted_alternatives = supabase_alternatives
                        question.save(update_fields=['accepted_alternatives'])
                        self.stdout.write(
                            self.style.SUCCESS(f"問題ID {question.id}: 更新完了")
                        )
                    updated_count += 1
                else:
                    if options['dry_run']:
                        self.stdout.write(f"問題ID {question.id}: 変更なし")
                        
            except requests.exceptions.Timeout:
                failed_count += 1
                error_msg = f"問題ID {question.id} タイムアウト"
                errors.append(error_msg)
            except requests.exceptions.RequestException as e:
                failed_count += 1
                error_msg = f"問題ID {question.id} ネットワークエラー: {str(e)}"
                errors.append(error_msg)
            except Exception as e:
                failed_count += 1
                error_msg = f"問題ID {question.id} エラー: {str(e)}"
                errors.append(error_msg)
        
        # 結果を表示
        self.stdout.write('\n' + '='*50)
        self.stdout.write('同期結果:')
        self.stdout.write(f'  更新件数: {updated_count}')
        self.stdout.write(f'  失敗件数: {failed_count}')
        
        if errors:
            self.stdout.write('\nエラー詳細:')
            for error in errors[:10]:  # 最初の10件のみ表示
                self.stdout.write(f'  - {error}')
            if len(errors) > 10:
                self.stdout.write(f'  ... 他 {len(errors) - 10} 件のエラー')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\n※ ドライランモードです。実際の更新は行われていません。')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n同期が完了しました。')
            )
