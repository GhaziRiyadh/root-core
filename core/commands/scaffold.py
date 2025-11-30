import os
import re
import shutil
from typing import Optional
import typer
from sqlmodel import select

from core.cli_entry import app
from core.config import settings
from core.database import get_local_session
from core.apps.auth.models.permission import Permission
from core.utils.utils import get_app_paths


# ---------------------------
# Helpers
# ---------------------------
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
    # Assuming this file is in core/commands/scaffold.py
    # We need to go up to src/apps/<app_name>
    # core/commands/scaffold.py -> core/commands -> core -> src -> src/apps
    
    # Adjust based on actual structure. 
    # If core is in root-core/core, and apps are in root-core/core/apps (as seen in file list)
    # But wait, the file list showed d:\projects\core\root-core\core\apps
    
    # The original cli.py was in root-core/cli.py.
    # It did: os.path.join(project_root, "src", "apps", app_name)
    # But the file list shows core/apps.
    
    # Let's check the file list again.
    # d:\projects\core\root-core\core\apps
    
    # So if I am in d:\projects\core\root-core\core\commands\scaffold.py
    # I need to go up to core, then into apps.
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.dirname(os.path.dirname(current_dir)) # core/commands -> core -> root-core (if core is top level)
    
    # Wait, d:\projects\core\root-core\core is the core package.
    # d:\projects\core\root-core\core\apps is where apps are.
    
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


# ---------------------------
# Commands
# ---------------------------
@app.command()
def app_create(app_name: str):
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


@app.command()
def model(
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


@app.command()
def full(
    app_name: str,
    model_name: str,
    fields: Optional[str] = typer.Option(
        None, "--fields", "-f", help="Fields in format 'name:type,name:type'"
    ),
):
    """Create a full app with one model + repo + service + router."""
    app_create(app_name)
    model(app_name, model_name, fields)


@app.command()
def list_apps():
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


@app.command()
def delete_app(
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


@app.command()
def delete_model(
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


@app.command()
def generate_permissions():
    """Generate permissions based on models in the app."""
    routers = get_app_paths("routers")
    import importlib.util

    resources: dict[str, list[str]] = {"admin": ["dashboard"]}
    for app_name, app_routers in routers.items():
        for router in app_routers.values():
            spec = importlib.util.spec_from_file_location("resource_name", router)
            resources_module = importlib.util.module_from_spec(spec)  # type: ignore
            spec.loader.exec_module(resources_module)  # type: ignore

            if app_name not in resources:
                resources[app_name] = []

            resources[app_name].append(resources_module.resource_name)

    print(f"🔍 Found routers: {resources}")

    for app_name, app_resources in resources.items():
        for res in app_resources:
            print(f"🔍 Processing resource: {res}")
            stmt = select(Permission).where(
                Permission.action.in_([act.value for act in settings.ACTIONS]),  # type: ignore
                Permission.resource == res,
                Permission.app_name == app_name,
            )
            session_gen = get_local_session()
            session = next(session_gen)  # type: ignore
            try:
                result = session.exec(stmt)
                permission_obj = result.all()
                existing_perms = {p.action for p in permission_obj}
                for action in settings.ACTIONS:
                    if action.value not in existing_perms:
                        new_perm = Permission(
                            action=action.value, resource=res, app_name=app_name
                        )
                        session.add(new_perm)
                        print(f"✅ Created permission: {action} - {res} - {app_name}")

                session.commit()
            finally:
                session.close()
