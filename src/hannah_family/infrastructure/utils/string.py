def format_cmd(cmd: list, *args, **kwargs):
    return "\0".join(cmd).format(*args, **kwargs).split("\0")
