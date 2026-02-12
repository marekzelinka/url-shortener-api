import random
from hashlib import md5


def generate_url_ident(url: str, length: int) -> str:
    """Returns a unique identifier for the given URL with the given length."""
    digest = md5(url.encode()).hexdigest()
    return "".join(random.choices(digest, k=length))
