from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()

# Import models so they are registered with SQLAlchemy
from .trail import Trail
from .location import Location
from .user import User  


__all__ = ['db', 'Trail', 'Location', 'User']
