from core.bases.base_command import BaseCommand


class CleanCommand(BaseCommand):
    def execute(self, *args, **kwargs):
        """Clean temporary files."""
        import shutil
        import os

        temp_dirs = ["__pycache__", ".pytest_cache", "build", "dist", ".mypy_cache"]

        for root, dirs, files in os.walk("src"):
            for dir_name in dirs:
                if dir_name in temp_dirs:
                    dir_path = os.path.join(root, dir_name)
                    shutil.rmtree(dir_path)
                    print(f"🗑️  Removed temporary directory: {dir_path}")

        print("✅ Cleaned temporary files.")