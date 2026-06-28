import sqlite3

DB_NAME = "bot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db() -> None:
    connection = get_connection()
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
    connection.close()


if __name__ == "__main__":
    init_db()
    print("База данных создана и готова к работе.")