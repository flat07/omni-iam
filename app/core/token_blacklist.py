from app.core.redis import redis_client


BLACKLIST_PREFIX = "blacklist:"


def blacklist_jti(jti: str, expires_in: int):
    key = f"{BLACKLIST_PREFIX}{jti}"
    redis_client.setex(key, expires_in, "1")


def is_jti_blacklisted(jti: str) -> bool:
    key = f"{BLACKLIST_PREFIX}{jti}"
    return redis_client.exists(key) == 1