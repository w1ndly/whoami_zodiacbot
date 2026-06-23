USER_SUBSCRIPTION = {}   # 59₽ — безлимит проверок
USER_SIGN_ACCESS = {}    # 290₽ — доступ к знаку

FREE_LIMIT = 10


# -------------------
# SUBSCRIPTION (59₽)
# -------------------

def get_subscription(user_id: int) -> bool:
    return USER_SUBSCRIPTION.get(user_id, False)


def set_subscription(user_id: int):
    USER_SUBSCRIPTION[user_id] = True


def check_free_limit(user_id: int, usage: int) -> bool:
    if get_subscription(user_id):
        return True

    return usage < FREE_LIMIT


# -------------------
# SIGN ACCESS (290₽)
# -------------------

def has_sign_access(user_id: int, sign: str) -> bool:
    return USER_SIGN_ACCESS.get(user_id, set()).__contains__(sign)


def grant_sign_access(user_id: int, sign: str):
    if user_id not in USER_SIGN_ACCESS:
        USER_SIGN_ACCESS[user_id] = set()

    USER_SIGN_ACCESS[user_id].add(sign)


def can_view_premium(user_id: int, sign: str) -> bool:
    return has_sign_access(user_id, sign)


# -------------------
# STATUS
# -------------------

def get_user_status(user_id: int, usage: int):
    return {
        "subscription": get_subscription(user_id),
        "limit": FREE_LIMIT,
        "usage": usage,
        "signs": len(USER_SIGN_ACCESS.get(user_id, []))
    }