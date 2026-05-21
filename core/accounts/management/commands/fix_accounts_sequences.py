from django.core.management.base import BaseCommand

from accounts.db_utils import reset_pg_id_sequences


class Command(BaseCommand):
    help = "همگام‌سازی sequenceهای id جداول accounts (رفع خطای duplicate pkey)"

    def handle(self, *args, **options):
        reset_pg_id_sequences()
        self.stdout.write(self.style.SUCCESS("Sequences به‌روز شدند."))
