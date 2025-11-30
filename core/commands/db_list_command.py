"""
Database list command - shows all discovered app databases.
"""
import typer
from core.bases.base_command import BaseCommand
from core.database_registry import discover_all_app_databases


class DbListCommand(BaseCommand):
    def execute(self):
        """
        List all discovered app databases.
        
        Shows database URLs for all apps based on:
        - Environment variables (<APP_NAME>_DATABASE_URL)
        - App's database.py files
        - Default DATABASE_URL
        
        Example:
            python cli.py db-list
        """
        print("📊 Discovered App Databases")
        print("=" * 50)
        
        app_databases = discover_all_app_databases()
        
        if not app_databases:
            print("\\nNo app databases configured")
            return
        
        print(f"\\nFound {len(app_databases)} app database(s):\\n")
        
        for app_name, db_url in app_databases.items():
            print(f"🔹 {app_name}")
            print(f"   URL: {db_url}")
            print()
