import os
from .BaseController import BaseController

class LessonController(BaseController):
    def __init__(self,):
        super().__init__()   
    
    def get_lesson_path(self, lesson_id):
        lesson_dir = os.path.join(self.file_dir, lesson_id)
        os.makedirs(lesson_dir, exist_ok=True)
        return lesson_dir
    
    