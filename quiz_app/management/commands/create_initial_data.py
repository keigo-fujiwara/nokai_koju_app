from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz_app.models import Subject, Unit
from accounts.models import StudentProfile, AdminProfile

User = get_user_model()


class Command(BaseCommand):
    help = '初期データを作成します'

    def handle(self, *args, **options):
        self.stdout.write('初期データを作成中...')
        
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
                self.stdout.write(f'教科を作成: {subject.label_ja}')
            else:
                self.stdout.write(f'教科は既に存在: {subject.label_ja}')
        
        # 単元データの作成
        units_data = [
            {'subject_code': 'science', 'grade_year': '中1', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中1', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中1', 'category': '生物'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '生物'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '生物'},
            {'subject_code': 'social', 'grade_year': '中1', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中1', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中2', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中2', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '公民'},
        ]
        
        for unit_data in units_data:
            subject = Subject.objects.get(code=unit_data['subject_code'])
            unit, created = Unit.objects.get_or_create(
                subject=subject,
                grade_year=unit_data['grade_year'],
                category=unit_data['category']
            )
            if created:
                self.stdout.write(f'単元を作成: {unit}')
            else:
                self.stdout.write(f'単元は既に存在: {unit}')
        
        # 管理者ユーザーの作成
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
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
            self.stdout.write('管理者ユーザーを作成: admin (パスワード: admin123)')
        else:
            self.stdout.write('管理者ユーザーは既に存在: admin')
        
        # テスト用生徒ユーザーの作成
        student_user, created = User.objects.get_or_create(
            username='student001',
            defaults={
                'email': 'student001@example.com',
                'role': User.Role.STUDENT,
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
            self.stdout.write('テスト生徒ユーザーを作成: student001 (パスワード: student123)')
        else:
            self.stdout.write('テスト生徒ユーザーは既に存在: student001')
        
        self.stdout.write(self.style.SUCCESS('初期データの作成が完了しました！'))
