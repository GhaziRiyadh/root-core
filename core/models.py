"""
Auto-discover and import all models from apps for Alembic migrations.

This module automatically finds and imports all model files from the APPS_DIR,
ensuring that Alembic can detect all models for migration generation.
"""
from core.utils.utils import convert_path_to_model, get_app_paths
import importlib

# Get all model paths from all apps using APPS_DIR configuration
exits_one = []
paths = get_app_paths("models").values()

for path in paths:
    for p in path.values():
        if p in exits_one:
            continue
        exits_one.append(p)
        try:
            importlib.import_module(name=convert_path_to_model(p))
        except Exception as e:
            print(f"⚠️  Failed to import model from {p}: {e}")

print(f"✅ Loaded {len(exits_one)} model files from APPS_DIR:")
for e in exits_one:
    print(f"   - {e}")
