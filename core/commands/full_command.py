from typing import Optional
import typer
from core.bases.base_command import BaseCommand
from core.commands.app_create_command import AppCreateCommand
from core.commands.model_command import ModelCommand

class FullCommand(BaseCommand):
    def execute(
        self,
        app_name: str,
        model_name: str,
        fields: Optional[str] = typer.Option(
            None, "--fields", "-f", help="Fields in format 'name:type,name:type'"
        ),
    ):
        """Create a full app with one model + repo + service + router."""
        # We can instantiate and run other commands
        AppCreateCommand(command_name="app_create").execute(app_name)
        ModelCommand(command_name="model").execute(app_name, model_name, fields)
