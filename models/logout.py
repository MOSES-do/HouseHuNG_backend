#!/usr/bin/python3
""" holds user token for logout purpose"""

import models
from models.base_model import BaseModel, Base
import sqlalchemy
from sqlalchemy import Column, String, Integer


class TokenBlacklist(BaseModel, Base):
    __tablename__ = 'token_blacklist'
    jti = Column(String(120), nullable=False, unique=True)
