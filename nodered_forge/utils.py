import re
import random


def to_js_package_name(s):
    # Replace spaces with hyphens
    s = s.strip().replace(' ', '-').replace('_', '-')

    # Remove special characters and spaces
    s = re.sub(r'[^a-zA-Z0-9-]', '', s)
    # Convert to lowercase
    s = s.lower()

    return s[:50]


def generate_bright_color(seed_string):
    # Use the hash function to generate a hash value from the input string
    hash_value = sum(ord(char) for char in seed_string)

    # Create a custom random instance for each thread
    local_random = random.Random(hash_value)
    red, green, blue = 0, 0, 0
    # Generate random values for RGB components with high luminance
    while red + green + blue < 300:
        red = local_random.randint(0, 255)
        green = local_random.randint(0, 255)
        blue = local_random.randint(0, 255)

    # Format the RGB values into a hex color code
    color_code = "#{:02X}{:02X}{:02X}".format(red, green, blue)

    return color_code


def normalize_icon(icon):
    icon = icon.strip()

    if icon.startswith('fa-'):
        icon = 'font-awesome/' + icon

    return icon
