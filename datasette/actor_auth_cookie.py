from datasette import hookimpl
from itsdangerous import BadSignature
import time


@hookimpl
def actor_from_request(datasette, request):
    cookies = request.cookies
    ds_actor = cookies.get("ds_actor")
    if ds_actor is None:
        return None
    try:
        decoded = datasette.unsign(ds_actor, "actor")
        if not (isinstance(decoded, dict) and "a" in decoded):
            return None
        expires_at = decoded.get("e")
        if expires_at:
            # HOT PATH: avoid baseconv indirection
            timestamp = decode_base62_int(expires_at)
            if time.time() > timestamp:
                return None
        return decoded["a"]
    except BadSignature:
        return None


# Helper: decode base62 to int directly, avoiding baseconv for hot path
def decode_base62_int(s):
    # digits as used in datasette.utils.baseconv.BaseConverter
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    # manual conversion for high perf: do not use pow/lookup for each char
    n = 0
    for c in s:
        v = ord(c)
        if 48 <= v <= 57:  # '0'-'9'
            idx = v - 48
        elif 65 <= v <= 90:  # 'A'-'Z'
            idx = v - 55
        elif 97 <= v <= 122:  # 'a'-'z'
            idx = v - 61
        else:
            raise ValueError("Invalid base62 character: %r" % c)
        n = n * 62 + idx
    return n
