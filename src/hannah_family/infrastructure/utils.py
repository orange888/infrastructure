from re import compile

ENV_PATTERN = compile(r"([A-Z_]+)=([^;]+);")


def parse_env(output: str):
    return {name: value for name, value in ENV_PATTERN.findall(output)}
