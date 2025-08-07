from application import db
import logging


class BaseService:
    """Base service class with common methods."""
    
    def __init__(self):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)