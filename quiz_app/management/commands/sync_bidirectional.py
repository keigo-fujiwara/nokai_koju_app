import os
import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from quiz_app.models import Question, Subject, Unit
from datetime import datetime


class Command(BaseCommand):
    help = 'DjangoとSupabaseの双方向同期を行います'

    def add_arguments(self, parser):
        parser.add_argument(
            '--direction',
            type=str,
            choices=['django-to-supabase', 'supabase-to-django', 'bidirectional'],
            default='bidirectional',
            help='同期の方向を指定'
        )
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
        
        direction = options['direction']
        subject_filter = options['subject']
        dry_run = options['dry_run']
        
        self.stdout.write(f'同期方向: {direction}')
        self.stdout.write(f'対象教科: {subject_filter or "全教科"}')
        self.stdout.write(f'ドライラン: {dry_run}')
        
        if direction in ['django-to-supabase', 'bidirectional']:
            self.sync_django_to_supabase(headers, subject_filter, dry_run)
        
        if direction in ['supabase-to-django', 'bidirectional']:
            self.sync_supabase_to_django(headers, subject_filter, dry_run)
    
    def sync_django_to_supabase(self, headers, subject_filter, dry_run):
        """DjangoからSupabaseへの同期"""
        self.stdout.write('\n=== Django → Supabase 同期開始 ===')
        
        questions = Question.objects.all()
        if subject_filter:
            questions = questions.filter(unit__subject__code=subject_filter)
        
        updated_count = 0
        failed_count = 0
        errors = []
        
        for question in questions:
            try:
                # Supabaseのデータを取得
                response = requests.get(
                    f"{supabase_url}/rest/v1/quiz_app_question?id=eq.{question.id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code != 200:
                    failed_count += 1
                    errors.append(f"問題ID {question.id} 取得失敗 ({response.status_code})")
                    continue
                
                supabase_data = response.json()
                if not supabase_data:
                    # Supabaseにデータが存在しない場合は作成
                    if not dry_run:
                        self.create_supabase_question(headers, question)
                    updated_count += 1
                    self.stdout.write(f"問題ID {question.id}: Supabaseに新規作成")
                    continue
                
                # データを比較して更新
                supabase_question = supabase_data[0]
                update_data = self.prepare_update_data(question, supabase_question)
                
                if update_data:
                    if not dry_run:
                        response = requests.patch(
                            f"{supabase_url}/rest/v1/quiz_app_question?id=eq.{question.id}",
                            headers=headers,
                            json=update_data,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            updated_count += 1
                            self.stdout.write(f"問題ID {question.id}: 更新完了")
                        else:
                            failed_count += 1
                            errors.append(f"問題ID {question.id} 更新失敗 ({response.status_code})")
                    else:
                        updated_count += 1
                        self.stdout.write(f"問題ID {question.id}: 更新予定")
                else:
                    if dry_run:
                        self.stdout.write(f"問題ID {question.id}: 変更なし")
                        
            except Exception as e:
                failed_count += 1
                errors.append(f"問題ID {question.id} エラー: {str(e)}")
        
        self.stdout.write(f'\nDjango → Supabase 同期結果:')
        self.stdout.write(f'  更新件数: {updated_count}')
        self.stdout.write(f'  失敗件数: {failed_count}')
        
        if errors:
            self.stdout.write('\nエラー詳細:')
            for error in errors[:10]:
                self.stdout.write(f'  - {error}')
    
    def sync_supabase_to_django(self, headers, subject_filter, dry_run):
        """SupabaseからDjangoへの同期"""
        self.stdout.write('\n=== Supabase → Django 同期開始 ===')
        
        # Supabaseから全データを取得
        try:
            response = requests.get(
                f"{supabase_url}/rest/v1/quiz_app_question",
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f'Supabaseからのデータ取得に失敗しました: {response.status_code}')
                )
                return
            
            supabase_questions = response.json()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Supabaseからのデータ取得エラー: {str(e)}')
            )
            return
        
        updated_count = 0
        failed_count = 0
        errors = []
        
        for supabase_question in supabase_questions:
            try:
                question_id = supabase_question.get('id')
                if not question_id:
                    continue
                
                # Djangoのデータを取得
                try:
                    django_question = Question.objects.get(id=question_id)
                except Question.DoesNotExist:
                    failed_count += 1
                    errors.append(f"問題ID {question_id} Djangoに存在しません")
                    continue
                
                # 教科フィルター
                if subject_filter and django_question.unit.subject.code != subject_filter:
                    continue
                
                # データを比較して更新
                update_fields = self.prepare_django_update(django_question, supabase_question)
                
                if update_fields:
                    if not dry_run:
                        for field, value in update_fields.items():
                            setattr(django_question, field, value)
                        django_question.save()
                        updated_count += 1
                        self.stdout.write(f"問題ID {question_id}: 更新完了")
                    else:
                        updated_count += 1
                        self.stdout.write(f"問題ID {question_id}: 更新予定")
                else:
                    if dry_run:
                        self.stdout.write(f"問題ID {question_id}: 変更なし")
                        
            except Exception as e:
                failed_count += 1
                errors.append(f"問題ID {question_id} エラー: {str(e)}")
        
        self.stdout.write(f'\nSupabase → Django 同期結果:')
        self.stdout.write(f'  更新件数: {updated_count}')
        self.stdout.write(f'  失敗件数: {failed_count}')
        
        if errors:
            self.stdout.write('\nエラー詳細:')
            for error in errors[:10]:
                self.stdout.write(f'  - {error}')
    
    def prepare_update_data(self, django_question, supabase_question):
        """DjangoデータをSupabase用に準備"""
        update_data = {}
        
        # 基本フィールドの比較
        fields_to_sync = [
            'text', 'correct_answer', 'parts_count', 'requires_unit_label',
            'unit_label_text', 'question_type', 'choices', 'accepted_alternatives'
        ]
        
        for field in fields_to_sync:
            django_value = getattr(django_question, field, None)
            supabase_value = supabase_question.get(field)
            
            # JSONFieldの処理
            if field in ['choices', 'accepted_alternatives']:
                if isinstance(django_value, str):
                    try:
                        django_value = json.loads(django_value)
                    except json.JSONDecodeError:
                        django_value = []
                
                if isinstance(supabase_value, str):
                    try:
                        supabase_value = json.loads(supabase_value)
                    except json.JSONDecodeError:
                        supabase_value = []
            
            if django_value != supabase_value:
                update_data[field] = django_value
        
        return update_data
    
    def prepare_django_update(self, django_question, supabase_question):
        """SupabaseデータをDjango用に準備"""
        update_fields = {}
        
        # 基本フィールドの比較
        fields_to_sync = [
            'text', 'correct_answer', 'parts_count', 'requires_unit_label',
            'unit_label_text', 'question_type', 'choices', 'accepted_alternatives'
        ]
        
        for field in fields_to_sync:
            django_value = getattr(django_question, field, None)
            supabase_value = supabase_question.get(field)
            
            # JSONFieldの処理
            if field in ['choices', 'accepted_alternatives']:
                if isinstance(django_value, str):
                    try:
                        django_value = json.loads(django_value)
                    except json.JSONDecodeError:
                        django_value = []
                
                if isinstance(supabase_value, str):
                    try:
                        supabase_value = json.loads(supabase_value)
                    except json.JSONDecodeError:
                        supabase_value = []
            
            if django_value != supabase_value:
                update_fields[field] = supabase_value
        
        return update_fields
    
    def create_supabase_question(self, headers, question):
        """Supabaseに新しい問題を作成"""
        create_data = {
            'id': question.id,
            'text': question.text,
            'correct_answer': question.correct_answer,
            'parts_count': question.parts_count,
            'requires_unit_label': question.requires_unit_label,
            'unit_label_text': question.unit_label_text,
            'question_type': question.question_type,
            'choices': question.choices,
            'accepted_alternatives': question.accepted_alternatives,
            'unit_id': question.unit.id,
            'source_id': question.source_id,
            'created_at': question.created_at.isoformat() if question.created_at else None,
            'updated_at': question.updated_at.isoformat() if question.updated_at else None
        }
        
        response = requests.post(
            f"{supabase_url}/rest/v1/quiz_app_question",
            headers=headers,
            json=create_data,
            timeout=30
        )
        
        return response.status_code == 201
