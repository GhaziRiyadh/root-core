import os
from typing import Optional
import typer
from core.bases.base_command import BaseCommand
from core.commands.utils import get_base_path, to_snake_case, write_file

class ModelCommand(BaseCommand):
    def execute(
        self,
        app_name: str,
        model_name: str,
        fields: Optional[str] = typer.Option(
            None,
            "--fields",
            "-f",
            help="Fields in format 'name:type,name:type'",
        ),
    ):
        """Create model + repository + service + router + schemas for this model."""
        if not model_name.isidentifier():
            print("❌ Invalid model name. Use only letters, numbers, and underscores.")
            raise typer.Exit(1)

        base_path = get_base_path(app_name)
        model_name_snake = to_snake_case(model_name)

        # Parse fields if provided
        field_list = []
        if fields:
            for field in fields.split(","):
                field = field.strip()
                if ":" in field:
                    name, file_type = field.split(":", 1)
                    field_list.append((name.strip(), file_type.strip()))

        # ---------------------------
        # Model
        # ---------------------------
        model_file = os.path.join(base_path, "models", f"{model_name_snake}.py")
        model_content = f'''"""{model_name} model."""

from sqlmodel import Field
from core.database import BaseModel


class {model_name}(BaseModel, table=True):
    """{model_name} model class."""
    
    __tablename__ = "{app_name}_{model_name_snake}s"  # type: ignore
'''

        # Add fields
        if field_list:
            for field_name, field_type in field_list:
                model_content += f"    {field_name}: {field_type} = Field()\n"
        else:
            model_content += "    # Add your fields here\n"
            model_content += "    name: str = Field()\n"

        model_content += "\n"
        write_file(model_file, model_content)

        # ---------------------------
        # Schemas
        # ---------------------------
        schemas_file = os.path.join(base_path, "schemas", f"{model_name_snake}.py")
        schemas_content = f'''"""{model_name} schemas."""

from typing import Optional
from pydantic import BaseModel


class {model_name}Create(BaseModel):
    """Schema for creating a {model_name_snake}."""
'''

        if field_list:
            for field_name, field_type in field_list:
                schemas_content += f"    {field_name}: {field_type}\n"
        else:
            schemas_content += "    name: str\n"

        schemas_content += f'''

class {model_name}Update(BaseModel):
    """Schema for updating a {model_name_snake}."""
'''

        if field_list:
            for field_name, field_type in field_list:
                # Make all fields optional for update
                schemas_content += f"    {field_name}: Optional[{field_type}] = None\n"
        else:
            schemas_content += "    name: Optional[str] = None\n"

        schemas_content += "\n"
        write_file(schemas_file, schemas_content)

        # ---------------------------
        # Repository
        # ---------------------------
        repo_file = os.path.join(
            base_path, "repositories", f"{model_name_snake}_repository.py"
        )
        repo_content = f'''"""{model_name} repository."""

from core.bases.base_repository import BaseRepository
from core.apps.{app_name}.models.{model_name_snake} import {model_name}


class {model_name}Repository(BaseRepository[{model_name}]):
    """{model_name} repository class."""
    
    model = {model_name}
'''
        write_file(repo_file, repo_content)

        # ---------------------------
        # Service
        # ---------------------------
        service_file = os.path.join(base_path, "services", f"{model_name_snake}_service.py")
        service_content = f'''"""{model_name} service."""

from typing import Any, Dict
from core.bases.base_service import BaseService
from core.apps.{app_name}.repositories.{model_name_snake}_repository import {model_name}Repository
from core.apps.{app_name}.models.{model_name_snake} import {model_name}


class {model_name}Service(BaseService[{model_name}]):
    """{model_name} service class."""
    repository: {model_name}Repository
    
    def __init__(self, repository: {model_name}Repository) -> None:
        self.repository = repository
'''
        write_file(service_file, service_content)

        # ---------------------------
        # Router
        # ---------------------------
        router_file = os.path.join(base_path, "routers", f"{model_name_snake}_router.py")
        router_content = f'''"""{model_name} router."""

from core.database import get_session
from core.bases.crud_api import CRUDApi
from core.apps.{app_name}.services.{model_name_snake}_service import {model_name}Service
from core.apps.{app_name}.repositories.{model_name_snake}_repository import {model_name}Repository
from core.apps.{app_name}.schemas.{model_name_snake} import {model_name}Create, {model_name}Update

resource_name: str = "{model_name_snake.replace('_', '-')}s"

def get_{model_name_snake}_repository():
    """Get {model_name_snake} repository instance."""
    return {model_name}Repository(get_session) #type:ignore


def get_{model_name_snake}_service():
    """Get {model_name_snake} service instance."""
    repository = get_{model_name_snake}_repository()
    return {model_name}Service(repository)


class {model_name}Router(CRUDApi):
    """{model_name} router class."""
    
    def __init__(self):
        super().__init__(
            service=get_{model_name_snake}_service(),
            create_schema={model_name}Create,
            update_schema={model_name}Update,
            prefix="/{model_name_snake.replace('_', '-')}s",
            tags=["{model_name.title()}s"],
            resource_name=resource_name,
        )


# Router instance
router = {model_name}Router()
'''
        write_file(router_file, router_content)

        # ---------------------------
        # Update app __init__.py to export the router
        # ---------------------------
        app_init_file = os.path.join(base_path, "__init__.py")
        export_line = f"\nfrom .routers.{model_name_snake}_router import router as {model_name_snake}_router\napi_routers.append({model_name_snake}_router)\n"

        app_init_content = ""
        if os.path.exists(app_init_file):
            with open(app_init_file, "r") as f:
                app_init_content = f.read()
        else:
            app_init_content = '"""{} app."""\n\napi_routers = []\n'.format(
                app_name.title()
            )

        # Read existing content and append if not already there
        if os.path.exists(app_init_file):
            with open(app_init_file, "r") as f:
                content = f.read()

            if export_line not in content:
                with open(app_init_file, "a") as f:
                    f.write(export_line)
        else:
            with open(app_init_file, "w") as f:
                f.write(export_line)

        print(f"🎉 Model '{model_name}' added to app '{app_name}' successfully.")
        print(f"📁 Files created:")
        print(f"   - models/{model_name_snake}.py")
        print(f"   - schemas/{model_name_snake}.py")
        print(f"   - repositories/{model_name_snake}_repository.py")
        print(f"   - services/{model_name_snake}_service.py")
        print(f"   - routers/{model_name_snake}_router.py")
