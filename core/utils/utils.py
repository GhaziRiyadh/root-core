import os, time
from typing import Dict, List


def get_apps(apps: list[list[str]] | None = None) -> Dict[str, str]:
    if apps is None:
        apps_dirs = [os.path.join("src", "apps")]
    else:
        apps_dirs = [os.path.join("src", *app) for app in apps]

    return {
        name: os.path.join(apps_dir, name)
        for apps_dir in apps_dirs
        for name in os.listdir(apps_dir)
        if os.path.isdir(os.path.join(apps_dir, name)) and not name.startswith("__")
    }


_cache: dict[str, tuple[float, dict[str, dict[str, str]]]] = {}
_CACHE_TTL = 60 * 60  # ثانية


def get_app_paths(
    child_name: str,
    app: list[list[str]] | None = None,
) -> dict[str, dict[str, str]]:
    """Return all <child_name> paths inside every app with TTL cache."""
    now = time.time()
    if child_name in _cache:
        ts, data = _cache[child_name]
        if now - ts < _CACHE_TTL:
            return data

    result: dict[str, dict[str, str]] = {}

    for app_name, app_path in get_apps(app).items():
        if not os.path.isdir(app_path) or app_name.startswith("__"):
            continue

        for root, dirs, files in os.walk(app_path):
            if os.path.basename(root) == child_name:
                file_paths = {
                    file.replace(".py", ""): os.path.join(root, file)
                    for file in files
                    if "__init__" not in file
                }
                result[app_name] = file_paths
                break

    _cache[child_name] = (now, result)
    return result


def convert_path_to_model(path: str):
    return path.replace("\\", ".").removesuffix(".py")


def calc_average_rate(reviews):
    return float(sum(r.rating for r in reviews) / len(reviews)) if reviews else 0


def get_current_app(file_path: str) -> str | None:
    """Return the app name that contains the given filesystem path, or None.

    Resolves absolute paths and symlinks and uses os.path.commonpath to avoid
    false positives from simple substring checks.
    """
    file_abs = os.path.realpath(os.path.abspath(file_path))

    for app_name, app_path in get_apps().items():
        app_abs = os.path.realpath(os.path.abspath(app_path))
        if not os.path.exists(app_abs):
            continue
        try:
            common_path = os.path.commonpath(
                [os.path.join(file_abs, app_name), app_abs]
            )

            if common_path == app_abs:
                return app_name
        except ValueError:
            # In case paths are on different drives (Windows) or invalid
            continue

    return None
