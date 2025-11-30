import os
import shutil
import typer
from core.bases.base_command import BaseCommand
from core.commands.utils import get_base_path

class DeleteAppCommand(BaseCommand):
    def execute(
        self,
        app_name: str,
        force: bool = typer.Option(
            False, "--force", "-f", help="Force delete without confirmation"
        ),
    ):
        """Delete an entire app directory."""
        base_path = get_base_path(app_name)

        if not os.path.exists(base_path):
            print(f"❌ App '{app_name}' does not exist.")
            raise typer.Exit(1)

        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to delete the app '{app_name}' and all its contents?"
            )
            if not confirm:
                print("❌ Deletion cancelled.")
                raise typer.Exit(0)

        shutil.rmtree(base_path)
        print(f"🗑️  App '{app_name}' deleted successfully.")
