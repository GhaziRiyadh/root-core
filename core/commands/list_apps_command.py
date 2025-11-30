import os
from core.bases.base_command import BaseCommand
from core.commands.utils import get_base_path

class ListAppsCommand(BaseCommand):
    def execute(self):
        """List all existing apps."""
        base_path = os.path.join(get_base_path(""), "..")  # Go up from an apps directory
        apps_path = os.path.join(base_path, "apps")

        if not os.path.exists(apps_path):
            print("❌ No apps directory found.")
            return

        apps = [
            d
            for d in os.listdir(apps_path)
            if os.path.isdir(os.path.join(apps_path, d)) and not d.startswith("_")
        ]

        if not apps:
            print("📁 No apps found.")
            return

        print("📁 Existing apps:")
        for _app in apps:
            app_path = os.path.join(apps_path, _app)
            models_path = os.path.join(app_path, "models")
            models = []

            if os.path.exists(models_path):
                models = [
                    f.replace(".py", "")
                    for f in os.listdir(models_path)
                    if f.endswith(".py") and not f.startswith("_")
                ]

            print(f"  🏷️  {_app}:")
            for _model in models:
                print(f"     📄 {_model}")
