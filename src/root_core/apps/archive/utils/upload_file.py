import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable, Optional
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

from root_core.config import settings


async def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    """
    Asynchronously saves the uploaded file directly to the specified destination.
    """
    try:
        async with aiofiles.open(destination, "wb") as buffer:
            while chunk := await upload_file.read(
                1024
            ):  # Read in chunks asynchronously
                await buffer.write(chunk)
    finally:
        await upload_file.close()


async def save_upload_file_tmp(upload_file: UploadFile, destination: Path) -> Path:
    """
    Asynchronously saves the uploaded file to a temporary file, then moves it to the destination.
    Returns the final destination path.
    """
    if upload_file.filename is None:
        raise ValueError("الملف المرفوع يجب ان يكون لديه اسم.")

    suffix = Path(upload_file.filename).suffix
    with NamedTemporaryFile(
        delete=False, suffix=suffix
    ) as tmp:  # Temporary file must still use regular I/O
        async with aiofiles.open(tmp.name, "wb") as tmp_file:
            while chunk := await upload_file.read(1024):
                await tmp_file.write(chunk)

        tmp_path = Path(tmp.name)

    # Move the temporary file to the destination path
    shutil.move(str(tmp_path), destination)
    await upload_file.close()
    return destination


def generate_unique_filename(upload_file: UploadFile) -> str:
    """
    Generates a unique filename while preserving the original file extension.
    """
    if upload_file.filename is None:
        raise ValueError("الملف المرفوع يجب ان يكون لديه اسم.")

    suffix = Path(upload_file.filename).suffix
    unique_name = f"{uuid4()}{suffix}"
    return unique_name


async def handle_upload_file(
    upload_file: UploadFile,
    sub_path: Optional[str] = None,
    handler: Optional[Callable[[Path], None]] = None,
    delete_after_processing: bool = False,
) -> Path:
    """
    Handles the file upload process asynchronously by:
      1. Creating the upload directory from the UPLOAD_FOLDER environment variable.
      2. Generating a unique file name for the uploaded file.
      3. Saving the file temporarily and then moving it to the final destination.
      4. If a handler function is provided, it processes the saved file.
      5. Optionally, deletes the file after processing if delete_after_processing is True.

    Returns the final destination path.
    """
    # Get the base upload folder from the environment variable, defaulting to "uploads" if not set
    base_upload_folder = Path(settings.UPLOAD_FOLDER)
    base_upload_folder.mkdir(parents=True, exist_ok=True)

    # Generate a unique file name for the uploaded file
    unique_filename = generate_unique_filename(upload_file)

    # Determine the target folder, including the optional sub_path
    if sub_path:
        target_folder = base_upload_folder / sub_path
        target_folder.mkdir(parents=True, exist_ok=True)
    else:
        target_folder = base_upload_folder

    destination_path = target_folder / unique_filename

    # Save the uploaded file using a temporary file, then move it to the destination
    saved_file_path = await save_upload_file_tmp(upload_file, destination_path)

    # Process the saved file if a handler is provided
    if handler:
        (
            handler(saved_file_path)
            if callable(handler) and hasattr(handler, "__call__")
            else handler(saved_file_path)
        )

    # Optionally delete the file after processing
    if delete_after_processing:
        if saved_file_path.exists():
            saved_file_path.unlink()

    return saved_file_path
