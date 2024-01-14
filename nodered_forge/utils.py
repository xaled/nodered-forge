import re


def to_js_package_name(s):
    # Replace spaces with hyphens
    s = s.strip().replace(' ', '-').replace('_', '-')

    # Remove special characters and spaces
    s = re.sub(r'[^a-zA-Z0-9]', '', s)
    # Convert to lowercase
    s = s.lower()

    return s[:50]
