from application import db
import logging


class BaseService:
    """Base service class with common methods."""
    
    def __init__(self):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def commit_changes(self):
        """Commit database changes."""
        try:
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"Database commit failed: {str(e)}")
            raise
