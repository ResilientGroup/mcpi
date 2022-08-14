try:
    from collections.abc import Iterable  # noqa
except ImportError:
    from collections import Iterable  # noqa


def flatten(l):
    for e in l:
        if isinstance(e, Iterable) and not isinstance(e, str):
            for ee in flatten(e): yield ee
        else:
            yield e


def flatten_parameters(l):
    return ",".join(map(str, flatten(l)))


def flatten_parameters_to_bytestring(l):
    return b",".join(map(_misc_to_bytes, flatten(l)))


def _misc_to_bytes(m):
    return str(m).encode("utf8")
