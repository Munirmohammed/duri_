from datetime import datetime
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, DateTime, JSON, TEXT, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import func
from uuid import uuid4
#from sqlalchemy.sql.sqltypes import Boolean
from .db import Base
#from .schema import Visibility, Nb_Category

""" 
    Notes:
        -  https://docs.sqlalchemy.org/en/14/orm/extensions/associationproxy.html#simplifying-association-objects
"""
