from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz_app.models import Subject, Unit, Question
from accounts.models import StudentProfile, AdminProfile
import os
import sqlite3
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'ローカル環境のSQLiteデータをRenderのPostgreSQLに移行します'

    def handle(self, *args, **options):
        self.stdout.write('🚀 ローカルSQLiteからRenderへのデータ移行開始...')
        
        try:
            # SQLiteファイルのパス
            sqlite_path = 'db.sqlite3'
            
            if not os.path.exists(sqlite_path):
                self.stdout.write(self.style.ERROR(f'❌ SQLiteファイルが見つかりません: {sqlite_path}'))
                return
            
            # SQLiteに接続
            self.stdout.write(f'📂 SQLiteファイルに接続: {sqlite_path}')
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            
            # 1. 既存のデータをクリア（管理者ユーザーは保持）
            self.stdout.write('🗑️ 既存のデータをクリア中...')
            Question.objects.all().delete()
            Unit.objects.all().delete()
            Subject.objects.all().delete()
            
            # 2. SQLiteからデータを取得
            self.stdout.write('📥 SQLiteからデータを取得中...')
            
            # 教科データの取得
            cursor.execute('SELECT id, code, label_ja FROM quiz_app_subject')
            subjects_data = cursor.fetchall()
            self.stdout.write(f'📚 教科データ: {len(subjects_data)}件')
            
            # 単元データの取得
            cursor.execute('SELECT id, subject_id, grade_year, category FROM quiz_app_unit')
            units_data = cursor.fetchall()
            self.stdout.write(f'📖 単元データ: {len(units_data)}件')
            
            # 問題データの取得
            cursor.execute('''
                SELECT id, unit_id, source_id, question_type, text, correct_answer, 
                       accepted_alternatives, choices, requires_unit_label, unit_label_text
                FROM quiz_app_question
            ''')
            questions_data = cursor.fetchall()
            self.stdout.write(f'❓ 問題データ: {len(questions_data)}件')
            
            # 3. データをRenderのPostgreSQLに移行
            self.stdout.write('📤 RenderのPostgreSQLにデータを移行中...')
            
            # 教科データの移行
            subject_map = {}
            for subject_row in subjects_data:
                subject_id, code, label_ja = subject_row
                subject = Subject.objects.create(
                    id=subject_id,
                    code=code,
                    label_ja=label_ja
                )
                subject_map[subject_id] = subject
                self.stdout.write(f'✅ 教科作成: {subject.label_ja}')
            
            # 単元データの移行
            unit_map = {}
            for unit_row in units_data:
                unit_id, subject_id, grade_year, category = unit_row
                unit = Unit.objects.create(
                    id=unit_id,
                    subject=subject_map[subject_id],
                    grade_year=grade_year,
                    category=category
                )
                unit_map[unit_id] = unit
                self.stdout.write(f'✅ 単元作成: {unit}')
            
            # 問題データの移行
            created_count = 0
            for question_row in questions_data:
                try:
                    (question_id, unit_id, source_id, question_type, text, 
                     correct_answer, accepted_alternatives, choices, 
                     requires_unit_label, unit_label_text) = question_row
                    
                    # JSONフィールドの処理
                    accepted_alternatives_list = []
                    if accepted_alternatives:
                        try:
                            accepted_alternatives_list = json.loads(accepted_alternatives)
                        except:
                            accepted_alternatives_list = []
                    
                    choices_list = []
                    if choices:
                        try:
                            choices_list = json.loads(choices)
                        except:
                            choices_list = []
                    
                    question = Question.objects.create(
                        id=question_id,
                        unit=unit_map[unit_id],
                        source_id=source_id,
                        question_type=question_type,
                        text=text,
                        correct_answer=correct_answer,
                        accepted_alternatives=accepted_alternatives_list,
                        choices=choices_list,
                        requires_unit_label=bool(requires_unit_label),
                        unit_label_text=unit_label_text or ""
                    )
                    created_count += 1
                    if created_count % 50 == 0:
                        self.stdout.write(f'📝 問題作成進捗: {created_count}件')
                except Exception as e:
                    self.stdout.write(f'⚠️ 問題作成エラー (ID: {question_row[0] if question_row else "unknown"}): {e}')
                    continue
            
            # SQLite接続を閉じる
            conn.close()
            
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
            
            self.stdout.write(self.style.SUCCESS('🎉 ローカルデータの移行が完了しました！'))
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
