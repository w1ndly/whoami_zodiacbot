import os
import sqlite3
from datetime import datetime, date
from calendar import monthrange

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


def add_one_month(source_date: date) -> date:
    month = source_date.month + 1
    year = source_date.year

    if month > 12:
        month = 1
        year += 1

    last_day = monthrange(year, month)[1]
    day = min(source_date.day, last_day)

    return date(year, month, day)


def get_current_free_period_start(user_id: int) -> str:
    today = date.today()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT created_at FROM users WHERE user_id = ?",
            (user_id,)
        )

        row = cursor.fetchone()

    if row is None or row[0] is None:
        return today.isoformat()

    period_start = datetime.fromisoformat(row[0]).date()

    while add_one_month(period_start) <= today:
        period_start = add_one_month(period_start)

    return period_start.isoformat()


def ensure_user_checks_period(user_id: int) -> None:
    current_period_start = get_current_free_period_start(user_id)

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT last_reset_at
            FROM user_checks
            WHERE user_id = ?
            """,
            (user_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return

        last_reset_at = row[0]

        if last_reset_at is None:
            cursor.execute(
                """
                UPDATE user_checks
                SET last_reset_at = ?
                WHERE user_id = ?
                """,
                (current_period_start, user_id)
            )

        elif last_reset_at < current_period_start:
            cursor.execute(
                """
                UPDATE user_checks
                SET used_checks = 0,
                    last_reset_at = ?
                WHERE user_id = ?
                """,
                (current_period_start, user_id)
            )

        connection.commit()


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

        cursor.execute("PRAGMA table_info(user_checks)")
        columns = [column[1] for column in cursor.fetchall()]

        if "last_reset_at" not in columns:
            cursor.execute(
                "ALTER TABLE user_checks ADD COLUMN last_reset_at TEXT"
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

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_bonus_checks (
                user_id INTEGER PRIMARY KEY,
                bonus_checks INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                telegram_payment_charge_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS robokassa_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pack_key TEXT NOT NULL,
                checks INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'created',
                created_at TEXT NOT NULL,
                paid_at TEXT
            )
            """
        )

        connection.commit()


def get_used_checks(user_id: int) -> int:
    ensure_user_checks_period(user_id)
    
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
    ensure_user_checks_period(user_id)
    current_period_start = get_current_free_period_start(user_id)

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO user_checks(user_id, used_checks, last_reset_at)
            VALUES(?, 1, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET used_checks = used_checks + 1
            """,
            (user_id, current_period_start)
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
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(amount), 0)
            FROM payments
            WHERE status = 'paid'
            """
        )
        payments_row = cursor.fetchone()

        payments_count = payments_row[0]
        stars_total = payments_row[1]

        if payments_count > 0:
            average_payment = round(stars_total / payments_count)
        else:
            average_payment = 0

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
        "payments_count": payments_count,
        "stars_total": stars_total,
        "average_payment": average_payment,
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

def get_bonus_checks(user_id: int) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT bonus_checks FROM user_bonus_checks WHERE user_id = ?",
            (user_id,)
        )

        row = cursor.fetchone()

    if row is None:
        return 0

    return row[0]


def add_bonus_checks(user_id: int, amount: int) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO user_bonus_checks(user_id, bonus_checks)
            VALUES(?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET bonus_checks = bonus_checks + excluded.bonus_checks
            """,
            (user_id, amount)
        )

        connection.commit()


def use_bonus_check(user_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT bonus_checks FROM user_bonus_checks WHERE user_id = ?",
            (user_id,)
        )

        row = cursor.fetchone()

        if row is None or row[0] <= 0:
            return False

        cursor.execute(
            """
            UPDATE user_bonus_checks
            SET bonus_checks = bonus_checks - 1
            WHERE user_id = ?
            """,
            (user_id,)
        )

        connection.commit()

    return True


def save_payment(
    user_id: int,
    telegram_payment_charge_id: str,
    payload: str,
    amount: int,
    currency: str,
    status: str = "paid",
) -> None:
    now = datetime.utcnow().isoformat()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO payments (
                user_id,
                telegram_payment_charge_id,
                payload,
                amount,
                currency,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                telegram_payment_charge_id,
                payload,
                amount,
                currency,
                status,
                now,
            )
        )

        connection.commit()

def create_robokassa_order(
    user_id: int,
    pack_key: str,
    checks: int,
    amount: int,
) -> int:
    now = datetime.utcnow().isoformat()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO robokassa_orders (
                user_id,
                pack_key,
                checks,
                amount,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, 'created', ?)
            """,
            (
                user_id,
                pack_key,
                checks,
                amount,
                now,
            )
        )

        connection.commit()

        return cursor.lastrowid


def get_robokassa_order(order_id: int) -> dict | None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                pack_key,
                checks,
                amount,
                status,
                created_at,
                paid_at
            FROM robokassa_orders
            WHERE id = ?
            """,
            (order_id,)
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "pack_key": row[2],
        "checks": row[3],
        "amount": row[4],
        "status": row[5],
        "created_at": row[6],
        "paid_at": row[7],
    }


def mark_robokassa_order_paid(order_id: int) -> None:
    now = datetime.utcnow().isoformat()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE robokassa_orders
            SET status = 'paid',
                paid_at = ?
            WHERE id = ?
            """,
            (now, order_id)
        )

        connection.commit()


def get_last_robokassa_orders(limit: int = 10) -> list[dict]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, user_id, pack_key, checks, amount, status, created_at, paid_at
            FROM robokassa_orders
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "user_id": row[1],
            "pack_key": row[2],
            "checks": row[3],
            "amount": row[4],
            "status": row[5],
            "created_at": row[6],
            "paid_at": row[7],
        }
        for row in rows
    ]


def get_telegram_payments_stats() -> dict:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(amount), 0)
            FROM payments
            WHERE currency = 'XTR'
              AND status = 'paid'
            """
        )

        row = cursor.fetchone()

    return {
        "paid_count": row[0],
        "stars_total": row[1],
    }


def get_last_telegram_payments(limit: int = 10) -> list[dict]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, user_id, payload, amount, currency, status, created_at
            FROM payments
            WHERE currency = 'XTR'
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "user_id": row[1],
            "payload": row[2],
            "amount": row[3],
            "currency": row[4],
            "status": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]


def get_robokassa_order_status_counts() -> dict:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT status, COUNT(*)
            FROM robokassa_orders
            GROUP BY status
            """
        )

        rows = cursor.fetchall()

    counts = {
        "created": 0,
        "paid": 0,
        "failed": 0,
    }

    for row in rows:
        counts[row[0]] = row[1]

    return counts


def get_robokassa_orders_by_status(
    status: str,
    limit: int = 10,
) -> list[dict]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, user_id, pack_key, checks, amount, status, created_at, paid_at
            FROM robokassa_orders
            WHERE status = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (status, limit),
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "user_id": row[1],
            "pack_key": row[2],
            "checks": row[3],
            "amount": row[4],
            "status": row[5],
            "created_at": row[6],
            "paid_at": row[7],
        }
        for row in rows
    ]


def get_all_payments() -> list[dict]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, user_id, telegram_payment_charge_id, payload, amount, currency, status, created_at
            FROM payments
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "user_id": row[1],
            "telegram_payment_charge_id": row[2],
            "payload": row[3],
            "amount": row[4],
            "currency": row[5],
            "status": row[6],
            "created_at": row[7],
        }
        for row in rows
    ]


def get_all_robokassa_orders() -> list[dict]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, user_id, pack_key, checks, amount, status, created_at, paid_at
            FROM robokassa_orders
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "user_id": row[1],
            "pack_key": row[2],
            "checks": row[3],
            "amount": row[4],
            "status": row[5],
            "created_at": row[6],
            "paid_at": row[7],
        }
        for row in rows
    ]


def get_last_combined_orders(limit: int = 10) -> list[dict]:
    orders = []

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, user_id, payload, amount, currency, status, created_at
            FROM payments
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        payment_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT id, user_id, pack_key, checks, amount, status, created_at, paid_at
            FROM robokassa_orders
            WHERE status != 'paid'
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        robokassa_rows = cursor.fetchall()

    for row in payment_rows:
        currency = row[4]

        source = "TG"
        if currency == "RUB":
            source = "RS"

        orders.append(
            {
                "source": source,
                "id": row[0],
                "user_id": row[1],
                "pack_key": row[2],
                "checks": None,
                "amount": row[3],
                "currency": row[4],
                "status": row[5],
                "created_at": row[6],
            }
        )

    for row in robokassa_rows:
        orders.append(
            {
                "source": "RS",
                "id": row[0],
                "user_id": row[1],
                "pack_key": row[2],
                "checks": row[3],
                "amount": row[4],
                "currency": "RUB",
                "status": row[5],
                "created_at": row[6],
            }
        )

    orders.sort(
        key=lambda order: order["created_at"],
        reverse=True
    )

    return orders[:limit]