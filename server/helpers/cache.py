from fastapi import Request


def cache_key_exclude_request(f, *args, **kwargs):
    """Build cache key from all args/kwargs except Request instances."""
    key_args = tuple(a for a in args if not isinstance(a, Request))
    key_kwargs = tuple(
        (k, v) for k, v in sorted(kwargs.items()) if not isinstance(v, Request)
    )
    return f"{f.__module__}.{f.__name__}:{key_args!r}:{key_kwargs!r}"
