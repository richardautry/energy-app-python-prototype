import re

PATTERN = re.compile(r'(?<!^)(?=[A-Z])')


def convert_camel_to_snake_case(text: str) -> str:
    return PATTERN.sub('_', text).lower()
