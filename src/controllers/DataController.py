from .BaseController import BaseController
from ..models import ResponseStatus

class DataController(BaseController):
    def __init__(self):
        super().__init__()  
        
    def validate_file(self, file):
        # Validate file type
        if not self.is_allowed_file(file.filename):
            return False, ResponseStatus.INVALID_FILE_TYPE.value, f"File type not allowed. Allowed types: {', '.join(self.settings.FILE_ALLOWED_EXTENSIONS)}"
        
        # Validate file size
        if not self.is_allowed_file_size(file):
            return False, ResponseStatus.FILE_TOO_LARGE.value, f"File size exceeds the maximum limit of {self.settings.MAX_FILE_SIZE_MB} MB."
        
        return True, ResponseStatus.SUCCESS.value, "Supported file type and size."
    
    def is_allowed_file(self, filename) -> bool:
        ext = filename.rsplit('.', 1)[-1].upper()
        return ext in self.settings.FILE_ALLOWED_EXTENSIONS
    def is_allowed_file_size(self, file) -> bool:
        file_size_mb = file.size / (1024 * 1024)  # Convert bytes to MB
        return file_size_mb <= self.settings.MAX_FILE_SIZE_MB 