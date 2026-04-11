
import os

from .BaseController import BaseController
from ..models import ResponseStatus
from .LessonContraller import LessonController
class DataController(BaseController):
    def __init__(self):
        super().__init__()  
        
    def validate_file(self, file):
        # Validate file type
        if not self.is_allowed_file(file.filename):
            return False, ResponseStatus.INVALID_FILE_TYPE.value
        # Validate file size
        if not self.is_allowed_file_size(file):
            return False, ResponseStatus.FILE_TOO_LARGE.value
        
        return True, ResponseStatus.SUCCESS.value
    
    def is_allowed_file(self, filename) -> bool:
        ext = filename.rsplit('.', 1)[-1].upper()
        return ext in self.settings.FILE_ALLOWED_EXTENSIONS
    def is_allowed_file_size(self, file) -> bool:
        file_size_mb = file.size / (1024 * 1024)  # Convert bytes to MB
        return file_size_mb <= self.settings.MAX_FILE_SIZE_MB 
    
    def gen_unique_filepath(self, filename, lesson_id):
        random_str = self.generate_random_string()
        name, ext = filename.rsplit('.', 1)
        lesson_path = LessonController().get_lesson_path(lesson_id)
        clean_file_name = self.get_clean_filename(name)
        new_file_path = os.path.join(lesson_path, f"{clean_file_name}_{random_str}.{ext}")
        
        while os.path.exists(new_file_path):
            random_str = self.generate_random_string()
            new_file_path = os.path.join(lesson_path, f"{clean_file_name}_{random_str}.{ext}")
        
        return  new_file_path, f"{clean_file_name}_{random_str}.{ext}" 
        
    def get_clean_filename(self, filename):
        clean_name = ''.join(e for e in filename if e.isalnum() or e in (' ', '_',)).rstrip()
        clean_name = clean_name.replace(' ', '_')
        return clean_name