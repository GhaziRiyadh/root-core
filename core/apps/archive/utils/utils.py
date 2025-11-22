from pathlib import Path
import mimetypes
from typing import List

from core.apps.archive.models.archive import Archive
from core.apps.archive.models.file import File
from ..config import archive_setting
from datetime import datetime, timezone


def get_file_type_by_extension(path: Path) -> str:
    return mimetypes.guess_type(path)[0] or "unknown"


def get_file_path_by_extension(path: Path):
    mime_type = mimetypes.guess_type(path)[0] or "unknown"

    if mime_type.startswith("image/"):
        return archive_setting.IMAGE_DIR
    elif mime_type.startswith("video/"):
        return archive_setting.VIDEO_DIR
    elif mime_type.startswith("audio/"):
        return archive_setting.AUDIO_DIR
    else:
        return archive_setting.DOCS_DIR


def generate_date_based_file_path(path: Path) -> Path:
    date_time = datetime.now(timezone.utc)
    return Path(
        f"{get_file_path_by_extension(path)}/{date_time.year}/{date_time.month}/{date_time.day}"
    )


def get_file_url(file: File | str):
    if isinstance(file, str):
        return f"{archive_setting.BASE_FILE_URL}/{file}"
    return f"{archive_setting.BASE_FILE_URL}/{file.src}"


async def archive_to_srcset(archive: Archive) -> List[dict]:
    """Convert Archive files to a srcset structure using stored file sizes.

    Each File in the archive should have a `size` field (stored as "{width}x{height}")
    which will be used to build width-based srcset descriptors (e.g. "... 800w").

    Return value is a list of dicts suitable for building a <picture> element or
    passing to templates. Each dict is either:
      - {"media": "(min-width:...)", "srcset": "url1 1200w, url2 800w, ..."}
      - {"src": "fallback_url", "alt": "..."}

    The function picks files for each breakpoint by choosing variants with width
    >= breakpoint if available (otherwise the largest available), and builds a
    srcset string containing all available variants with their width descriptors.
    """

    def _parse_size(size_str: str) -> tuple[int, int]:
        try:
            parts = size_str.lower().split("x")
            w = int(parts[0].strip())
            h = int(parts[1].strip()) if len(parts) > 1 else 0
            return w, h
        except Exception:
            return 0, 0

    # Build list of (file, width, height)
    parsed_files: List[tuple[File, int, int]] = []
    for f in archive.files:
        w, h = _parse_size(getattr(f, "size", ""))
        parsed_files.append((f, w, h))

    # Sort descending by width (largest first)
    parsed_files.sort(key=lambda t: t[1], reverse=True)

    if not parsed_files:
        return []

    # Build a full srcset string using all variants (largest -> smallest)
    full_srcset = ", ".join(
        f"{get_file_url(f)} {w}w" for f, w, _ in parsed_files if w > 0
    )
    # If none had a parsable width, fall back to simple list of URLs
    if not full_srcset:
        full_srcset = ", ".join(get_file_url(f) for f, _, _ in parsed_files)

    srcsets: List[dict] = []

    # Example breakpoints (min-width, media-query) - adjust per project needs
    breakpoints = [
        (1200, "(min-width:1200px)"),
        (800, "(min-width:800px)"),
        (480, "(min-width:480px)"),
    ]

    # For each breakpoint choose variants with width >= breakpoint; if none,
    # use the largest available variant for that breakpoint.
    for min_width, media in breakpoints:
        # variants with width >= min_width
        variants = [(f, w) for f, w, _ in parsed_files if w >= min_width]
        if not variants:
            # fall back to the largest available (first in parsed_files)
            variants = [(parsed_files[0][0], parsed_files[0][1])]

        # Build srcset for this breakpoint
        srcset_str = ", ".join(f"{get_file_url(f)} {w}w" for f, w in variants)
        srcsets.append({"media": media, "srcset": srcset_str})

    # Always include a fallback single <img> source (smallest available)
    smallest_file, smallest_w, smallest_h = parsed_files[-1]
    srcsets.append(
        {
            "src": get_file_url(smallest_file),
            "alt": getattr(smallest_file, "alt", "Image"),
        }
    )

    # Also include a full combined srcset for convenience (useful for <img srcset=>)
    srcsets.insert(0, {"srcset": full_srcset})

    return srcsets
