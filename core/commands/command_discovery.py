import os
import importlib.util
from pathlib import Path
from typing import List, Type
from core.bases.base_command import BaseCommand
from core.config import settings

def discover_app_commands() -> List[Type[BaseCommand]]:
    """
    Discover all command classes from app-specific command directories.
    
    Looks for commands in: <APPS_DIR>/<app_name>/commands/*.py
    Each command file should contain a class that inherits from BaseCommand.
    
    Returns:
        List of command classes found in app directories.
    """
    commands = []
    
    # Get the apps directory from settings
    apps_dir = settings.APPS_DIR
    
    # If APPS_DIR is relative, make it absolute from project root
    if not os.path.isabs(apps_dir):
        # Assuming we're in core/commands/command_discovery.py
        # Go up to project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        apps_dir = os.path.join(project_root, apps_dir)
    
    if not os.path.exists(apps_dir):
        print(f"⚠️  Apps directory not found: {apps_dir}")
        return commands
    
    # Iterate through each app directory
    for app_name in os.listdir(apps_dir):
        app_path = os.path.join(apps_dir, app_name)
        
        if not os.path.isdir(app_path) or app_name.startswith("_"):
            continue
        
        # Look for commands directory in the app
        commands_dir = os.path.join(app_path, "commands")
        
        if not os.path.exists(commands_dir) or not os.path.isdir(commands_dir):
            continue
        
        # Iterate through command files
        for filename in os.listdir(commands_dir):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue
            
            command_file = os.path.join(commands_dir, filename)
            
            try:
                # Load the module dynamically
                module_name = f"{app_name}.commands.{filename[:-3]}"
                spec = importlib.util.spec_from_file_location(module_name, command_file)
                
                if spec is None or spec.loader is None:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find all classes in the module that inherit from BaseCommand
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    if (
                        isinstance(attr, type) and
                        issubclass(attr, BaseCommand) and
                        attr is not BaseCommand
                    ):
                        commands.append(attr)
                        print(f"✅ Discovered command: {attr.__name__} from {app_name}")
                        
            except Exception as e:
                print(f"⚠️  Failed to load command from {command_file}: {e}")
                continue
    
    return commands
