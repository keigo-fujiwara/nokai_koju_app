from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz_app.models import Subject, Unit, Question
from accounts.models import StudentProfile, AdminProfile
import os
import requests
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Supabaseから直接データを取得してRenderのPostgreSQLに移行します'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Supabaseからデータを直接移行開始...')
        
        try:
            # Supabaseの設定を確認
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            self.stdout.write(f'🔍 環境変数確認:')
            self.stdout.write(f'  SUPABASE_URL: {supabase_url[:50] if supabase_url else "未設定"}...')
            self.stdout.write(f'  SUPABASE_ANON_KEY: {supabase_key[:20] if supabase_key else "未設定"}...')
            
            if not supabase_url or not supabase_key:
                self.stdout.write(self.style.ERROR('❌ Supabase環境変数が設定されていません'))
                self.stdout.write('SUPABASE_URL と SUPABASE_ANON_KEY を設定してください')
                return
            
            # 1. 既存のデータをクリア（管理者ユーザーは保持）
            self.stdout.write('🗑️ 既存のデータをクリア中...')
            Question.objects.all().delete()
            Unit.objects.all().delete()
            Subject.objects.all().delete()
            
            # 2. Supabaseからデータを取得
            self.stdout.write('📥 Supabaseからデータを取得中...')
            
            # ヘッダーの設定
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            self.stdout.write(f'🔗 接続URL: {supabase_url}/rest/v1/')
            
            # 教科データの取得
            subjects_url = f"{supabase_url}/rest/v1/quiz_app_subject"
            self.stdout.write(f'📚 教科データ取得URL: {subjects_url}')
            
            subjects_response = requests.get(subjects_url, headers=headers)
            
            self.stdout.write(f'📊 教科データレスポンス: {subjects_response.status_code}')
            if subjects_response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'❌ 教科データの取得に失敗: {subjects_response.status_code}'))
                self.stdout.write(f'レスポンス内容: {subjects_response.text}')
                return
            
            subjects_data = subjects_response.json()
            self.stdout.write(f'📚 教科データ: {len(subjects_data)}件')
            
            # 単元データの取得
            units_url = f"{supabase_url}/rest/v1/quiz_app_unit"
            self.stdout.write(f'📖 単元データ取得URL: {units_url}')
            
            units_response = requests.get(units_url, headers=headers)
            
            self.stdout.write(f'📊 単元データレスポンス: {units_response.status_code}')
            if units_response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'❌ 単元データの取得に失敗: {units_response.status_code}'))
                self.stdout.write(f'レスポンス内容: {units_response.text}')
                return
            
            units_data = units_response.json()
            self.stdout.write(f'📖 単元データ: {len(units_data)}件')
            
            # 問題データの取得
            questions_url = f"{supabase_url}/rest/v1/quiz_app_question"
            self.stdout.write(f'❓ 問題データ取得URL: {questions_url}')
            
            questions_response = requests.get(questions_url, headers=headers)
            
            self.stdout.write(f'📊 問題データレスポンス: {questions_response.status_code}')
            if questions_response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'❌ 問題データの取得に失敗: {questions_response.status_code}'))
                self.stdout.write(f'レスポンス内容: {questions_response.text}')
                return
            
            questions_data = questions_response.json()
            self.stdout.write(f'❓ 問題データ: {len(questions_data)}件')
            
            # データが0件の場合は終了
            if len(subjects_data) == 0 and len(units_data) == 0 and len(questions_data) == 0:
                self.stdout.write(self.style.WARNING('⚠️ すべてのデータが0件です'))
                self.stdout.write('Supabaseの設定またはデータの存在を確認してください')
                return
            
            # 3. データをRenderのPostgreSQLに移行
            self.stdout.write('📤 RenderのPostgreSQLにデータを移行中...')
            
            # 教科データの移行
            subject_map = {}
            for subject_data in subjects_data:
                subject = Subject.objects.create(
                    id=subject_data['id'],
                    code=subject_data['code'],
                    label_ja=subject_data['label_ja']
                )
                subject_map[subject_data['id']] = subject
                self.stdout.write(f'✅ 教科作成: {subject.label_ja}')
            
            # 単元データの移行
            unit_map = {}
            for unit_data in units_data:
                unit = Unit.objects.create(
                    id=unit_data['id'],
                    subject=subject_map[unit_data['subject_id']],
                    grade_year=unit_data['grade_year'],
                    category=unit_data['category']
                )
                unit_map[unit_data['id']] = unit
                self.stdout.write(f'✅ 単元作成: {unit}')
            
            # 問題データの移行
            created_count = 0
            for question_data in questions_data:
                try:
                    question = Question.objects.create(
                        id=question_data['id'],
                        unit=unit_map[question_data['unit_id']],
                        source_id=question_data['source_id'],
                        question_type=question_data['question_type'],
                        text=question_data['text'],
                        correct_answer=question_data['correct_answer'],
                        accepted_alternatives=question_data.get('accepted_alternatives', []),
                        choices=question_data.get('choices', []),
                        requires_unit_label=question_data.get('requires_unit_label', False),
                        unit_label_text=question_data.get('unit_label_text', '')
                    )
                    created_count += 1
                    if created_count % 50 == 0:
                        self.stdout.write(f'📝 問題作成進捗: {created_count}件')
                except Exception as e:
                    self.stdout.write(f'⚠️ 問題作成エラー (ID: {question_data.get("id", "unknown")}): {e}')
                    continue
            
            # 4. 管理者ユーザーの確認・作成
            self.stdout.write('👨‍💼 管理者ユーザーを確認中...')
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'role': User.Role.ADMIN,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                
                AdminProfile.objects.create(
                    user=admin_user,
                    name='システム管理者',
                    employee_number='ADMIN001',
                    email='admin@example.com'
                )
                self.stdout.write('✅ 管理者ユーザーを作成: admin (パスワード: admin123)')
            else:
                self.stdout.write('📝 管理者ユーザーは既に存在: admin')
            
            # 5. テスト用生徒ユーザーの確認・作成
            self.stdout.write('👨‍🎓 テスト生徒ユーザーを確認中...')
            student_user, created = User.objects.get_or_create(
                username='student001',
                defaults={
                    'email': 'student001@example.com',
                    'role': User.Role.STUDENT,
                    'is_active': True,
                }
            )
            if created:
                student_user.set_password('student123')
                student_user.save()
                
                StudentProfile.objects.create(
                    user=student_user,
                    member_id='12345678',
                    prefecture='東京都',
                    school='テスト中学校',
                    class_name='1年1組',
                    nickname='テスト太郎',
                    grade='中1'
                )
                self.stdout.write('✅ テスト生徒ユーザーを作成: student001 (パスワード: student123)')
            else:
                self.stdout.write('📝 テスト生徒ユーザーは既に存在: student001')
            
            # 6. 最終統計
            subject_count = Subject.objects.count()
            unit_count = Unit.objects.count()
            question_count = Question.objects.count()
            user_count = User.objects.count()
            
            self.stdout.write(self.style.SUCCESS('🎉 Supabaseデータの移行が完了しました！'))
            self.stdout.write(f'📊 統計:')
            self.stdout.write(f'  - 教科: {subject_count}件')
            self.stdout.write(f'  - 単元: {unit_count}件')
            self.stdout.write(f'  - 問題: {question_count}件 (移行: {created_count}件)')
            self.stdout.write(f'  - ユーザー: {user_count}件')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ エラーが発生しました: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
        
        self.stdout.write('✅ 移行完了')
