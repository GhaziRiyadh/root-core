import os
import typer
from core.bases.base_command import BaseCommand
from core.commands.utils import get_base_path, ensure_package, write_file

class AppCreateCommand(BaseCommand):
    def execute(self, app_name: str):
        """Create a new app directory structure."""
        if not app_name.isidentifier():
            print("❌ Invalid app name. Use only letters, numbers, and underscores.")
            raise typer.Exit(1)

        base_path = get_base_path(app_name)
        ensure_package(base_path)

        for folder in ["models", "repositories", "services", "routers", "schemas"]:
            ensure_package(os.path.join(base_path, folder))

        # Create __init__.py for the app
        app_init_content = f'''"""{app_name.title()} app."""\n\n
api_routers = []\n
        '''
        write_file(os.path.join(base_path, "__init__.py"), app_init_content)

        print(f"✅ App directory created at {base_path}")
