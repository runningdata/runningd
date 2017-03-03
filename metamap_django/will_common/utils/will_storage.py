# -*- coding: utf-8 -*
from django.core.files.storage import FileSystemStorage


class WillFileStorage(FileSystemStorage):
    # This method is actually defined in Storage
    def get_available_name(self, name):
        return name
