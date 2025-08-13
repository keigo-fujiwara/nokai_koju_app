from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz_app.models import Subject, Unit, Question
from accounts.models import StudentProfile, AdminProfile
import random

User = get_user_model()


class Command(BaseCommand):
    help = '完全な初期データを作成します（教科、単元、問題を含む）'

    def handle(self, *args, **options):
        self.stdout.write('🚀 完全な初期データを作成中...')
        
        # 教科データの作成
        subjects = [
            {'code': 'science', 'label_ja': '理科'},
            {'code': 'social', 'label_ja': '社会'},
        ]
        
        for subject_data in subjects:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults=subject_data
            )
            if created:
                self.stdout.write(f'✅ 教科を作成: {subject.label_ja}')
            else:
                self.stdout.write(f'📝 教科は既に存在: {subject.label_ja}')
        
        # 単元データの作成（Supabaseと同じ構成）
        units_data = [
            # 理科
            {'subject_code': 'science', 'grade_year': '中1', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中1', 'category': '生物'},
            {'subject_code': 'science', 'grade_year': '中1', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中1', 'category': '地学'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '生物'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '地学'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '生物'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '地学'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '自然科学'},
            # 社会
            {'subject_code': 'social', 'grade_year': '中1', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中1', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中2', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中2', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '公民'},
        ]
        
        created_units = []
        for unit_data in units_data:
            subject = Subject.objects.get(code=unit_data['subject_code'])
            unit, created = Unit.objects.get_or_create(
                subject=subject,
                grade_year=unit_data['grade_year'],
                category=unit_data['category']
            )
            if created:
                self.stdout.write(f'✅ 単元を作成: {unit}')
                created_units.append(unit)
            else:
                self.stdout.write(f'📝 単元は既に存在: {unit}')
                created_units.append(unit)
        
        # 問題データの作成
        self.stdout.write('📚 問題データを作成中...')
        total_questions = 0
        
        for unit in created_units:
            # 各単元に50-60問の問題を作成
            num_questions = random.randint(50, 60)
            
            for i in range(num_questions):
                question_type = random.choice(['text', 'choice'])
                
                if question_type == 'text':
                    # 記述問題
                    question = Question.objects.create(
                        unit=unit,
                        source_id=f"{unit.subject.code}_{unit.grade_year}_{unit.category}_{i+1:03d}",
                        question_type='text',
                        text=f"{unit.subject.label_ja} {unit.grade_year} {unit.category} 問題{i+1}",
                        correct_answer=f"正解{i+1}",
                        accepted_alternatives=[f"別解{i+1}_1", f"別解{i+1}_2"],
                        requires_unit_label=False,
                        unit_label_text=""
                    )
                else:
                    # 選択問題
                    choices = [
                        f"選択肢A_{i+1}",
                        f"選択肢B_{i+1}",
                        f"選択肢C_{i+1}",
                        f"選択肢D_{i+1}"
                    ]
                    question = Question.objects.create(
                        unit=unit,
                        source_id=f"{unit.subject.code}_{unit.grade_year}_{unit.category}_{i+1:03d}",
                        question_type='choice',
                        text=f"{unit.subject.label_ja} {unit.grade_year} {unit.category} 選択問題{i+1}",
                        correct_answer=f"選択肢A_{i+1}",
                        accepted_alternatives=[],
                        choices=choices,
                        requires_unit_label=False,
                        unit_label_text=""
                    )
                
                total_questions += 1
                
                if total_questions % 100 == 0:
                    self.stdout.write(f'📝 問題作成進捗: {total_questions}問完了')
        
        # 管理者ユーザーの作成
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
        
        # テスト用生徒ユーザーの作成
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
        
        # 最終統計
        subject_count = Subject.objects.count()
        unit_count = Unit.objects.count()
        question_count = Question.objects.count()
        user_count = User.objects.count()
        
        self.stdout.write(self.style.SUCCESS('🎉 完全な初期データの作成が完了しました！'))
        self.stdout.write(f'📊 統計:')
        self.stdout.write(f'  - 教科: {subject_count}件')
        self.stdout.write(f'  - 単元: {unit_count}件')
        self.stdout.write(f'  - 問題: {question_count}件')
        self.stdout.write(f'  - ユーザー: {user_count}件')
