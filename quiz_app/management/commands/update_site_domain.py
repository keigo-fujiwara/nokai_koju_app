from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = '開発環境用にSitesフレームワークのドメインを更新します'

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(id=1)
            site.domain = '127.0.0.1:8000'
            site.name = '能開高受用科目アプリ (開発環境)'
            site.save()
            self.stdout.write(
                self.style.SUCCESS(f'Site domain updated to: {site.domain}')
            )
        except Site.DoesNotExist:
            # Siteが存在しない場合は作成
            site = Site.objects.create(
                id=1,
                domain='127.0.0.1:8000',
                name='能開高受用科目アプリ (開発環境)'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Site created with domain: {site.domain}')
            )
