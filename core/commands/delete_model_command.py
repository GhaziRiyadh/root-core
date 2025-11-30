import os
import typer
from core.bases.base_command import BaseCommand
from core.commands.utils import get_base_path, to_snake_case

class DeleteModelCommand(BaseCommand):
    def execute(
        self,
        app_name: str,
        model_name: str,
        force: bool = typer.Option(
            False, "--force", "-f", help="Force delete without confirmation"
        ),
    ):
        """Delete a model and its associated files from an app."""
        if not model_name.isidentifier():
            print("❌ Invalid model name. Use only letters, numbers, and underscores.")
            raise typer.Exit(1)

        base_path = get_base_path(app_name)
        model_name_lower = to_snake_case(model_name)

        files_to_delete = [
            os.path.join(base_path, "models", f"{model_name_lower}.py"),
            os.path.join(base_path, "schemas", f"{model_name_lower}.py"),
            os.path.join(base_path, "repositories", f"{model_name_lower}_repository.py"),
            os.path.join(base_path, "services", f"{model_name_lower}_service.py"),
            os.path.join(base_path, "routers", f"{model_name_lower}_router.py"),
        ]

        existing_files = [f for f in files_to_delete if os.path.exists(f)]

        if not existing_files:
            print(f"❌ No files found for model '{model_name}' in app '{app_name}'.")
            raise typer.Exit(1)

        if not force:
            print("The following files will be deleted:")
            for f in existing_files:
                print(f"  - {f}")
            confirm = typer.confirm("Are you sure you want to proceed?")
            if not confirm:
                print("❌ Deletion cancelled.")
                raise typer.Exit(0)

        for f in existing_files:
            os.remove(f)
            print(f"🗑️  Deleted: {f}")

        # Optionally, remove an import line from app __init__.py
        app_init_file = os.path.join(base_path, "__init__.py")
        if os.path.exists(app_init_file):
            with open(app_init_file, "r") as f:
                lines = f.readlines()

            import_line = f"from .routers.{model_name_lower}_router import router as {model_name_lower}_router\n"
            if import_line in lines:
                lines.remove(import_line)
                with open(app_init_file, "w") as f:
                    f.writelines(lines)
                print(f"🗑️  Removed import line from {app_init_file}")

        print(
            f"✅ Model '{model_name}' and its files deleted from app '{app_name}' successfully."
        )
