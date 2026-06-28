import sqlite3

DB_NAME = "bot.db"


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
    init_db()
    print("База данных создана и готова к работе.")