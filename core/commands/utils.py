import os
import re

def to_snake_case(name):
    # Add an underscore before each uppercase letter that is followed by a lowercase letter
    # (e.g., "CamelCase" -> "Camel_Case")
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)

    # Add an underscore before each uppercase letter that is preceded by a lowercase letter or digit
    # (e.g., "camelCase" -> "camel_Case", "HTTPStatus" -> "HTTP_Status")
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)

    # Replace spaces, hyphens, and multiple underscores with a single underscore
    name = re.sub(r"[\s-]+", "_", name)

    # Convert the entire string to lowercase
    return name.lower()


def get_base_path(app_name: str) -> str:
    # Get the absolute path of the CLI script
    # We need to go up to core/apps/<app_name>
    
    # Assuming this file is in core/commands/utils.py
    # core/commands/utils.py -> core/commands -> core
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.dirname(os.path.dirname(current_dir)) 
    
    return os.path.join(core_dir, "core", "apps", app_name)


def write_file(path: str, content: str):
    """Create a file if it does not exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"✅ Created: {path}")


def ensure_package(path: str):
    """Ensure a folder exists and has an __init__.py."""
    os.makedirs(path, exist_ok=True)
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write('"""Package initializer."""\n\n')
