import os
import sqlite3

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


if __name__ == "__main__":
    print_database_debug_info()
    init_db()
    print("База данных создана и готова к работе.")