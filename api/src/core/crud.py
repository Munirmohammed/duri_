from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects import postgresql as pg
from . import schema, tables
from .crud_base import CRUDBase


class User(CRUDBase):
    pass

class Workspace(CRUDBase):
    def filter_in(self):
        pass

class Team(CRUDBase):
    pass