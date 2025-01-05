from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models
from .trail import Trail
from .location import Location

__all__ = ['db', 'Trail', 'Location']
