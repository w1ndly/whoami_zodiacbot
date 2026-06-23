# product_layer.py

from datetime import datetime

FREE_LIMIT = 10

USER_USAGE = {}
USER_PLAN = {}


def get_user_plan(user_id: int) -> str:
    return USER_PLAN.get(user_id, "free")


def set_user_premium(user_id: int):
    USER_PLAN[user_id] = "premium"


def get_usage(user_id: int) -> int:
    return USER_USAGE.get(user_id, 0)


def add_usage(user_id: int):
    USER_USAGE[user_id] = get_usage(user_id) + 1


def reset_usage(user_id: int):
    USER_USAGE[user_id] = 0


def check_free_limit(user_id: int) -> bool:
    if get_user_plan(user_id) == "premium":
        return True

    return get_usage(user_id) < FREE_LIMIT


def can_access_premium(user_id: int) -> bool:
    return get_user_plan(user_id) == "premium"


def get_user_status(user_id: int) -> dict:
    return {
        "plan": get_user_plan(user_id),
        "usage": get_usage(user_id),
        "limit": FREE_LIMIT,
        "remaining": max(0, FREE_LIMIT - get_usage(user_id))
    }