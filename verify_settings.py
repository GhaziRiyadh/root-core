import os
import sys

# Add current dir to sys.path so we can import the custom settings file
sys.path.append(os.getcwd())

# Define a custom settings file
with open("test_custom_settings.py", "w", encoding="utf-8") as f:
    f.write(
        """
from core.config import Settings
class CustomSettings(Settings):
    CUSTOM_SETTING: str = "custom_value_test"
"""
    )

# Set the environment variable
os.environ["CORE_SETTINGS_CLASS"] = "test_custom_settings.CustomSettings"

try:
    # We need to reload the module or ensure it's loaded AFTER the env var is set
    # Since core.config initializes settings on import, we must import it now
    from core.config import settings, Settings

    print(f"Loaded settings type: {type(settings)}")

    is_custom = "test_custom_settings.CustomSettings" in str(type(settings))
    has_field = (
        hasattr(settings, "CUSTOM_SETTING")
        and settings.CUSTOM_SETTING == "custom_value_test"
    )

    if is_custom and has_field:
        print("SUCCESS: Custom settings class loaded and field verified.")
    else:
        print(f"FAILURE: Custom settings not loaded correctly.")
        print(f"Is custom type: {is_custom}")
        print(f"Has custom field: {has_field}")
        if has_field:
            print(f"Field value: {getattr(settings, 'CUSTOM_SETTING', 'N/A')}")

finally:
    # Cleanup
    if os.path.exists("test_custom_settings.py"):
        os.remove("test_custom_settings.py")
