import re

def validate_project_name(name: str) -> bool:
    if not name or len(name) < 3 or len(name) > 50:
        return False
    pattern = r'^[a-zA-Z0-9\s\-_\.]+$'
    return bool(re.match(pattern, name))

def validate_description(description: str) -> bool:
    if not description or len(description) < 20:
        return False
    if len(description) > 2000:
        return False
    return True