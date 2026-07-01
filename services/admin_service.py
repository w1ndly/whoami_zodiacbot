import os


def get_admin_ids() -> set[int]:
    raw_ids = os.getenv("ADMIN_IDS", "")

    if not raw_ids:
        raw_ids = os.getenv("ADMIN_ID", "")

    admin_ids = set()

    for raw_id in raw_ids.split(","):
        raw_id = raw_id.strip()

        if raw_id.isdigit():
            admin_ids.add(int(raw_id))

    return admin_ids


def is_admin(user_id: int) -> bool:
    return user_id in get_admin_ids()