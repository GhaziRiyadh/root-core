from enum import Enum


class ImageSize(tuple, Enum):
    # General images in the educational platform
    HERO = (1920, 1080)
    COURSE_THUMBNAIL = (800, 600)
    LESSON_THUMBNAIL = (400, 300)

    # User images
    USER_AVATAR = (150, 150)
    INSTRUCTOR_AVATAR = (200, 200)

    # Educational content images
    SLIDE_IMAGE = (1280, 720)
    VIDEO_PREVIEW = (640, 360)
    DOCUMENT_PREVIEW = (1024, 768)

    def get_size(self):
        return self.value

    def __str__(self):
        # Return like 200x200
        return f"{self.value[0]}x{self.value[1]}"
