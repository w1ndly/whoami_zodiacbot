import os
import sqlite3
from datetime import datetime

volume_path = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")

if volume_path:
    DB_NAME = os.path.join(volume_path, "bot.db")
else:
    DB_NAME = os.getenv("DATABASE_PATH", "bot.db")

def print_database_debug_info() -> None:
    print("=== DATABASE DEBUG ===")
    print(f"DATABASE_PATH: {os.getenv('DATABASE_PATH')}")
    print(f"RAILWAY_VOLUME_MOUNT_PATH: {os.getenv('RAILWAY_VOLUME_MOUNT_PATH')}")
    print(f"DB_NAME: {DB_NAME}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Database file exists: {os.path.exists(DB_NAME)}")

    db_dir = os.path.dirname(DB_NAME)

    if db_dir:
        print(f"Database directory: {db_dir}")
        print(f"Database directory exists: {os.path.exists(db_dir)}")
        print(f"Database directory writable: {os.access(db_dir, os.W_OK)}")

    print("======================")


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_checks (
                user_id INTEGER PRIMARY KEY,
                used_checks INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language_code TEXT,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS check_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                check_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.commit()


def get_used_checks(user_id: int) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT used_checks FROM user_checks WHERE user_id = ?",
            (user_id,)
        )

        row = cursor.fetchone()

    if row is None:
        return 0

    return row[0]


def increment_used_checks(user_id: int) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO user_checks(user_id, used_checks)
            VALUES(?, 1)
            ON CONFLICT(user_id)
            DO UPDATE SET used_checks = used_checks + 1
            """,
            (user_id,)
        )

        connection.commit()


def register_user(
    user_id: int,
    username: str | None,
    first_name: str | None,
    language_code: str | None,
) -> None:
    now = datetime.utcnow().isoformat()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (
                user_id,
                username,
                first_name,
                language_code,
                created_at,
                last_activity
            )
            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                language_code = excluded.language_code,
                last_activity = excluded.last_activity
            """,
            (
                user_id,
                username,
                first_name,
                language_code,
                now,
                now,
            )
        )

        connection.commit()


def get_user(user_id: int) -> dict | None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                user_id,
                username,
                first_name,
                language_code,
                created_at,
                last_activity
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "user_id": row[0],
        "username": row[1],
        "first_name": row[2],
        "language_code": row[3],
        "created_at": row[4],
        "last_activity": row[5],
    }

def reset_user_checks(user_id: int) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE user_checks
            SET used_checks = 0
            WHERE user_id = ?
            """,
            (user_id,)
        )

        connection.commit()

if __name__ == "__main__":
    print_database_debug_info()
    init_db()
    print("База данных создана и готова к работе.")

def get_users_statistics() -> dict:
    from datetime import datetime, timedelta

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM check_events")
        total_checks = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM check_events WHERE substr(created_at, 1, 10) = ?",
            (today.isoformat(),)
        )
        checks_today = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM check_events WHERE substr(created_at, 1, 10) >= ?",
            (week_ago.isoformat(),)
        )
        checks_week = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM check_events WHERE substr(created_at, 1, 10) >= ?",
            (month_ago.isoformat(),)
        )
        checks_month = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE substr(created_at, 1, 10) = ?",
            (today.isoformat(),)
        )
        new_today = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE substr(created_at, 1, 10) >= ?",
            (week_ago.isoformat(),)
        )
        new_week = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE substr(created_at, 1, 10) >= ?",
            (month_ago.isoformat(),)
        )
        new_month = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE substr(last_activity, 1, 10) = ?",
            (today.isoformat(),)
        )
        active_today = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE substr(last_activity, 1, 10) >= ?",
            (week_ago.isoformat(),)
        )
        active_week = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE substr(last_activity, 1, 10) >= ?",
            (month_ago.isoformat(),)
        )
        active_month = cursor.fetchone()[0]

    return {
        "total": total,
        "total_checks": total_checks,
        "checks_today": checks_today,
        "checks_week": checks_week,
        "checks_month": checks_month,
        "new_today": new_today,
        "new_week": new_week,
        "new_month": new_month,
        "active_today": active_today,
        "active_week": active_week,
        "active_month": active_month,

    }

def add_check_event(user_id: int, check_type: str) -> None:
    now = datetime.utcnow().isoformat()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO check_events (
                user_id,
                check_type,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                check_type,
                now,
            )
        )

        connection.commit()