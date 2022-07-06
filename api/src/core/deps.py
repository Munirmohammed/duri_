from typing import Generator
from .db import SessionLocal

class MySuperContextManager:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

def get_db():
    with MySuperContextManager() as db:
        yield db
    """ try:
        db = SessionLocal()
        yield db
    finally:
        db.close() """