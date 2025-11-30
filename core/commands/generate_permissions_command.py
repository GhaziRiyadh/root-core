from sqlmodel import select
from core.bases.base_command import BaseCommand
from core.config import settings
from core.database import get_local_session
from core.apps.auth.models.permission import Permission
from core.utils.utils import get_app_paths

class GeneratePermissionsCommand(BaseCommand):
    def execute(self):
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
