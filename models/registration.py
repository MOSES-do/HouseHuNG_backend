#!/usr/bin/python3
""" holds class User"""

import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class Registration(BaseModel, Base):
    """Representation of a user """
    __tablename__ = 'register_user'
    email = Column(String(128), nullable=False)
    password_hash = Column(String(1000), nullable=True)
    #users = relationship("", backref="user")

    def has_password(self):
        """Check if the user has a password set."""
        return self.password_hash is not None

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        #if self.set_password:
        return check_password_hash(self.password_hash, password)

