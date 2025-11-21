from pathlib import Path
from typing import List
import aiofiles
from PIL import Image
from PIL.Image import Resampling
from pydantic import BaseModel
from io import BytesIO
from src.core.apps.archive.utils.image_sizes import ImageSize


class ImageSizeReturnSchema(BaseModel):
    path: Path
    size: "ImageSize"


class AsyncImageProcessor:
    @staticmethod
    async def resize_and_save_all(image_path: Path) -> List[ImageSizeReturnSchema]:
        """
        Asynchronously resizes the image to all predefined sizes while maintaining aspect ratio.
        :param image_path: Path to the original image
        :return: List of ImageSizeReturnSchema with paths and sizes
        """
        result: List[ImageSizeReturnSchema] = []

        # Open image in context manager to ensure proper resource handling
        with Image.open(image_path) as img:
            img_format = img.format or "PNG"
            base_path = image_path.parent / image_path.stem
            base_path.mkdir(parents=True, exist_ok=True)

            for size_type in ImageSize:
                target_size = size_type.get_size()
                img_resized = img.copy()
                img_resized.thumbnail(target_size, Resampling.LANCZOS)

                output_path = (
                    base_path / f"{image_path.stem}_{size_type.name}{image_path.suffix}"
                )

                buffer = BytesIO()
                img_resized.save(buffer, format=img_format)
                buffer.seek(0)
                async with aiofiles.open(output_path, "wb") as f:
                    await f.write(buffer.read())

                result.append(
                    ImageSizeReturnSchema(
                        path=output_path,
                        size=size_type,
                    )
                )

        return result
