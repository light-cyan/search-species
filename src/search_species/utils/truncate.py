# pyright: strict


def truncate(name: str, maxlen: int):
    if len(name) <= maxlen:
        return name
    else:
        return name[:maxlen-3] + "..."
