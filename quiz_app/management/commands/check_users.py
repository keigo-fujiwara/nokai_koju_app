from django.core.management.base import BaseCommand
from accounts.models import User, AdminProfile


class Command(BaseCommand):
    help = '現在のユーザーの状態を確認します'

    def handle(self, *args, **options):
        self.stdout.write('=== ユーザー一覧 ===')
        
        users = User.objects.all().order_by('id')
        for user in users:
            self.stdout.write(f'ID: {user.pk}')
            self.stdout.write(f'  ユーザー名: {user.username}')
            self.stdout.write(f'  メール: {user.email}')
            self.stdout.write(f'  役割: {user.role}')
            self.stdout.write(f'  アクティブ: {user.is_active}')
            self.stdout.write(f'  作成日: {user.date_joined}')
            
            if hasattr(user, 'admin_profile'):
                admin_profile = user.admin_profile
                self.stdout.write(f'  管理者名: {admin_profile.name}')
                self.stdout.write(f'  社員番号: {admin_profile.employee_number}')
            
            self.stdout.write('---')
        
        # 非アクティブな管理者ユーザーを確認
        inactive_admins = User.objects.filter(role=User.Role.ADMIN, is_active=False)
        if inactive_admins.exists():
            self.stdout.write('=== 非アクティブな管理者ユーザー ===')
            for user in inactive_admins:
                self.stdout.write(f'ID: {user.pk}, ユーザー名: {user.username}, メール: {user.email}')
        else:
            self.stdout.write('非アクティブな管理者ユーザーはいません。')
