"""ابزارهای دیتابیس (همگام‌سازی sequence در PostgreSQL)."""

from django.db import connection


ACCOUNTS_SEQUENCE_TABLES = (
    "accounts_user",
    "accounts_profile",
    "accounts_otpcode",
)


def reset_pg_id_sequences(tables=ACCOUNTS_SEQUENCE_TABLES):
    """
    وقتی داده با SQL/restore وارد شده، sequence ممکن است عقب بماند و INSERT با id تکراری خطا دهد.
    sequence را با MAX(id) جدول همگام می‌کند.
    جدول خالی: next id = 1 (نه setval(0) که در PostgreSQL خطا می‌دهد).
    """
    if connection.vendor != "postgresql":
        return

    qn = connection.ops.quote_name
    with connection.cursor() as cursor:
        for table in tables:
            quoted = qn(table)
            cursor.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence(%s, 'id'),
                    (SELECT COALESCE(MAX(id), 1) FROM {quoted}),
                    (SELECT EXISTS (SELECT 1 FROM {quoted} LIMIT 1))
                )
                WHERE pg_get_serial_sequence(%s, 'id') IS NOT NULL
                """,
                [table, table],
            )
