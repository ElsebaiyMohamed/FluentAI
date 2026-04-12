
import os
import aiofiles

from .BaseController import BaseController
from ..models import ResponseStatus
from .LessonContraller import LessonController

class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_file(self, file):
        if not self.is_allowed_file(file.filename):
            return False, ResponseStatus.FILE_TYPE_NOT_SUPPORTED.value

        if not self.is_allowed_file_size(file):
            return False, ResponseStatus.FILE_SIZE_EXCEEDED.value

        return True, ResponseStatus.FILE_VALIDATED_SUCCESS.value

    def is_allowed_file(self, filename) -> bool:
        if not filename or '.' not in filename:
            return False

        ext = filename.rsplit('.', 1)[-1].upper()
        return ext in self.settings.FILE_ALLOWED_EXTENSIONS

    def is_allowed_file_size(self, file) -> bool:
        try:
            current_position = file.file.tell()
            file.file.seek(0, os.SEEK_END)
            file_size = file.file.tell()
            file.file.seek(current_position)
            return file_size <= self.settings.MAX_FILE_SIZE_MB * 1024 * 1024
        except Exception:
            return True

    async def save_file(self, upload_file, lesson_id):
        file_path, file_id = self.gen_unique_filepath(upload_file.filename, lesson_id)

        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await upload_file.read(self.settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(content)

        return file_path, file_id

    def gen_unique_filepath(self, filename, lesson_id):
        random_str = self.generate_random_string()
        name, ext = filename.rsplit('.', 1)
        lesson_path = LessonController().get_lesson_path(lesson_id)
        clean_file_name = self.get_clean_filename(name)
        new_file_name = f"{clean_file_name}_{random_str}.{ext}"
        new_file_path = os.path.join(lesson_path, new_file_name)

        while os.path.exists(new_file_path):
            random_str = self.generate_random_string()
            new_file_name = f"{clean_file_name}_{random_str}.{ext}"
            new_file_path = os.path.join(lesson_path, new_file_name)

        return new_file_path, new_file_name

    def get_clean_filename(self, filename):
        clean_name = ''.join(e for e in filename if e.isalnum() or e in (' ', '_')).rstrip()
        return clean_name.replace(' ', '_')
